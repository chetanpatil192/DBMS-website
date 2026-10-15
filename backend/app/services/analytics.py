"""Analytics service querying real MongoDB collections for dashboard metrics."""

import time
from typing import Any, Dict, List, Tuple

from pymongo.database import Database

from app.schemas.analytics import (
    CategoryPerformance,
    DashboardMetrics,
    OrderSummary,
    SalesPoint,
)
from app.services.base import BaseService


class AnalyticsService(BaseService):
    """Executes high-performance aggregation pipelines and queries against MongoDB."""

    def __init__(self, db: Database[Dict[str, Any]]) -> None:
        super().__init__(db)

    def get_dashboard_metrics(self) -> Tuple[DashboardMetrics, float, Dict[str, Any]]:
        """Retrieves core KPIs, recent orders, sales trend, and category breakdown.

        Returns:
            Tuple of (DashboardMetrics, db_duration_ms, diagnostics_dict).
        """
        start_db = time.perf_counter()

        # 1. Total counts
        total_customers = self.db.customers.count_documents({})
        total_orders = self.db.orders.count_documents({})

        # 2. Revenue & Average Order Value (ignoring cancelled orders)
        revenue_pipeline = [
            {"$match": {"status": {"$ne": "cancelled"}}},
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$total_amount"},
                    "avg_order_value": {"$avg": "$total_amount"},
                }
            },
        ]
        rev_result = list(self.db.orders.aggregate(revenue_pipeline))
        if rev_result:
            total_revenue = round(rev_result[0].get("total_revenue", 0.0), 2)
            avg_order_value = round(rev_result[0].get("avg_order_value", 0.0), 2)
        else:
            total_revenue = 0.0
            avg_order_value = 0.0

        # 3. Recent 8 orders (sorted by order_date DESC)
        recent_cursor = self.db.orders.find(
            {},
            {
                "_id": 0,
                "order_id": 1,
                "customer_id": 1,
                "customer_name": 1,
                "customer_email": 1,
                "region": 1,
                "order_date": 1,
                "status": 1,
                "payment_method": 1,
                "total_amount": 1,
                "items_count": 1,
            },
        ).sort("order_date", -1).limit(8)
        recent_orders = [OrderSummary(**doc) for doc in recent_cursor]

        # 4. Sales Trend (grouped by month or 30-day buckets)
        trend_pipeline = [
            {"$match": {"status": {"$ne": "cancelled"}}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m", "date": "$order_date"}},
                    "revenue": {"$sum": "$total_amount"},
                    "orders_count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        trend_cursor = self.db.orders.aggregate(trend_pipeline)
        sales_trend = [
            SalesPoint(
                period=doc["_id"],
                revenue=round(doc.get("revenue", 0.0), 2),
                orders_count=doc.get("orders_count", 0),
            )
            for doc in trend_cursor
            if doc.get("_id")
        ]

        # 5. Category Performance
        cat_pipeline = [
            {"$match": {"status": {"$ne": "cancelled"}}},
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.category",
                    "revenue": {"$sum": "$items.subtotal"},
                    "orders_count": {"$sum": 1},
                }
            },
            {"$sort": {"revenue": -1}},
            {"$limit": 5},
        ]
        cat_cursor = self.db.orders.aggregate(cat_pipeline)
        category_performance = [
            CategoryPerformance(
                category=doc["_id"],
                revenue=round(doc.get("revenue", 0.0), 2),
                orders_count=doc.get("orders_count", 0),
            )
            for doc in cat_cursor
            if doc.get("_id")
        ]

        db_duration_ms = round((time.perf_counter() - start_db) * 1000, 2)

        diagnostics = {
            "target_collections": ["orders", "customers"],
            "orders_aggregated": total_orders,
            "customers_counted": total_customers,
            "indexes_leveraged": ["idx_order_status_date", "idx_order_date_desc"],
            "db_engine_time_ms": db_duration_ms,
        }

        metrics = DashboardMetrics(
            total_customers=total_customers,
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_order_value=avg_order_value,
            recent_orders=recent_orders,
            sales_trend=sales_trend,
            category_performance=category_performance,
        )

        return metrics, db_duration_ms, diagnostics
