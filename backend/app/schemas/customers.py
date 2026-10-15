"""Pydantic schemas for customer listings and search."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CustomerItem(BaseModel):
    """Customer item representation for paginated directory."""

    customer_id: str
    name: str
    email: str
    phone: Optional[str] = None
    city: str
    country: str
    region: str
    total_spent: float
    order_count: int
    created_at: datetime
