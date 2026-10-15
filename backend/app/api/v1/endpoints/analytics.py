"""Analytics API endpoints for dashboard statistics and performance summaries."""

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.analytics import DashboardMetrics
from app.schemas.common import ResponseEnvelope, ResponseMeta
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    response_model=ResponseEnvelope[DashboardMetrics],
    summary="Dashboard Metrics & Analytical Summaries",
    description="Returns customer count, total orders, revenue, recent orders, sales trend, and category breakdown.",
)
def get_dashboard_metrics(
    db: Database[Dict[str, Any]] = Depends(get_db),
) -> ResponseEnvelope[DashboardMetrics]:
    """Calculates and returns real-time aggregation metrics directly from MongoDB."""
    start_total = time.perf_counter()
    service = AnalyticsService(db)
    metrics, db_duration_ms, diagnostics = service.get_dashboard_metrics()
    total_duration_ms = round((time.perf_counter() - start_total) * 1000, 2)
    api_overhead_ms = max(round(total_duration_ms - db_duration_ms, 2), 0.0)

    return ResponseEnvelope[DashboardMetrics](
        data=metrics,
        meta=ResponseMeta(
            execution_time_ms=total_duration_ms,
            db_execution_time_ms=db_duration_ms,
            api_overhead_ms=api_overhead_ms,
            query_diagnostics=diagnostics,
        ),
    )
