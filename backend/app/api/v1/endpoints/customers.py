"""Customer endpoints for paginated listing and text search."""

import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import PaginationMeta, ResponseEnvelope, ResponseMeta
from app.schemas.customers import CustomerItem
from app.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get(
    "",
    response_model=ResponseEnvelope[List[CustomerItem]],
    summary="List & Search Customers",
    description="Returns a paginated list of customers with optional search across name, email, or city.",
)
def list_customers(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Records per page"),
    search: Optional[str] = Query(default=None, description="Search term for name, email, or city"),
    sort_by: str = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Database[Dict[str, Any]] = Depends(get_db),
) -> ResponseEnvelope[List[CustomerItem]]:
    """Fetches paginated customers matching the search criteria with DB latency metrics."""
    start_total = time.perf_counter()
    service = CustomerService(db)
    customers, total_items, total_pages, db_duration_ms, diagnostics = service.list_customers(
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total_duration_ms = round((time.perf_counter() - start_total) * 1000, 2)
    api_overhead_ms = max(round(total_duration_ms - db_duration_ms, 2), 0.0)

    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )

    return ResponseEnvelope[List[CustomerItem]](
        data=customers,
        meta=ResponseMeta(
            execution_time_ms=total_duration_ms,
            db_execution_time_ms=db_duration_ms,
            api_overhead_ms=api_overhead_ms,
            query_diagnostics=diagnostics,
            pagination=pagination,
        ),
    )
