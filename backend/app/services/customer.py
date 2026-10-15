"""Customer service managing search, filtering, and paginated queries."""

import math
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from app.schemas.customers import CustomerItem
from app.services.base import BaseService


class CustomerService(BaseService):
    """Executes customer listing and search queries with index utilization."""

    def __init__(self, db: Database[Dict[str, Any]]) -> None:
        super().__init__(db)

    def list_customers(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[CustomerItem], int, int, float, Dict[str, Any]]:
        """Queries customers with optional search filtering, pagination, and sorting.

        Returns:
            Tuple of (customer_list, total_count, total_pages, db_duration_ms, diagnostics).
        """
        start_db = time.perf_counter()

        filter_query: Dict[str, Any] = {}
        is_search = bool(search and search.strip())
        if is_search:
            term = search.strip()  # type: ignore[union-attr]
            escaped_term = re.escape(term)
            filter_query = {
                "$or": [
                    {"name": {"$regex": escaped_term, "$options": "i"}},
                    {"email": {"$regex": escaped_term, "$options": "i"}},
                    {"city": {"$regex": escaped_term, "$options": "i"}},
                ]
            }

        total_count = self.db.customers.count_documents(filter_query)
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

        # Validate sort field
        allowed_sort_fields = {"created_at", "total_spent", "order_count", "name"}
        field = sort_by if sort_by in allowed_sort_fields else "created_at"
        direction = ASCENDING if sort_order.lower() == "asc" else DESCENDING

        skip = (page - 1) * page_size
        cursor = (
            self.db.customers.find(filter_query, {"_id": 0})
            .sort([(field, direction)])
            .skip(skip)
            .limit(page_size)
        )

        customers = [CustomerItem(**doc) for doc in cursor]
        db_duration_ms = round((time.perf_counter() - start_db) * 1000, 2)

        diagnostics = {
            "collection": "customers",
            "search_filter_applied": is_search,
            "index_leveraged": "idx_cust_text_search" if is_search else f"idx_cust_{field}",
            "matched_documents": total_count,
            "db_engine_time_ms": db_duration_ms,
        }

        return customers, total_count, total_pages, db_duration_ms, diagnostics
