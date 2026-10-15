"""Pydantic schemas for dashboard statistics and analytical summaries."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderSummary(BaseModel):
    """Compact order document representation for recent order tables."""

    order_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    region: str
    order_date: datetime
    status: str
    payment_method: str
    total_amount: float
    items_count: int


class SalesPoint(BaseModel):
    """Aggregate sales point for time-series chart."""

    period: str = Field(..., description="Date period string (e.g. '2024-05' or 'May 2024')")
    revenue: float = Field(..., description="Total revenue generated in this period")
    orders_count: int = Field(..., description="Number of orders placed in this period")


class CategoryPerformance(BaseModel):
    """Analytical summary by product category."""

    category: str
    revenue: float
    orders_count: int


class DashboardMetrics(BaseModel):
    """Aggregated core KPIs for the analytics dashboard."""

    total_customers: int
    total_orders: int
    total_revenue: float
    average_order_value: float
    recent_orders: List[OrderSummary]
    sales_trend: List[SalesPoint]
    category_performance: List[CategoryPerformance]
