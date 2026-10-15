"""Common Pydantic schemas for standardized API response envelopes and health checks."""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Metadata describing paginated collection results."""

    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, le=1000, description="Number of items per page")
    total_items: int = Field(..., ge=0, description="Total count of items matching the query")
    total_pages: int = Field(..., ge=0, description="Total number of available pages")


class ResponseMeta(BaseModel):
    """Standard metadata included in all successful API responses."""

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of response generation",
    )
    execution_time_ms: Optional[float] = Field(
        default=None,
        description="Total round-trip server processing time in milliseconds",
    )
    db_execution_time_ms: Optional[float] = Field(
        default=None,
        description="Dedicated MongoDB execution latency in milliseconds",
    )
    api_overhead_ms: Optional[float] = Field(
        default=None,
        description="FastAPI routing, validation, and serialization overhead in milliseconds",
    )
    query_diagnostics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Database indexing and execution plan diagnostics",
    )
    pagination: Optional[PaginationMeta] = Field(
        default=None,
        description="Pagination details when returning collections",
    )
    profiling: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional database executionStats or explain metrics",
    )


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standard wrapper for all successful API response bodies."""

    data: T = Field(..., description="The response payload")
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta,
        description="Response execution metadata and profiling info",
    )


class ErrorDetail(BaseModel):
    """Detailed error object contained within an ErrorEnvelope."""

    code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable error explanation")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Supplementary contextual attributes or validation failures",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when error occurred",
    )


class ErrorEnvelope(BaseModel):
    """Standard error response format for all 4xx and 5xx responses."""

    error: ErrorDetail = Field(..., description="Error detail container")


class DatabaseHealth(BaseModel):
    """Health and responsiveness status of the MongoDB instance."""

    connected: bool = Field(..., description="Whether a ping to MongoDB succeeded")
    latency_ms: float = Field(..., description="Round-trip ping latency in milliseconds")
    database: Optional[str] = Field(default=None, description="Active database name")
    error: Optional[str] = Field(default=None, description="Diagnostic error message if disconnected")


class HealthCheckResponse(BaseModel):
    """Application health status payload."""

    status: str = Field(..., description="Overall service status ('healthy', 'degraded', 'unhealthy')")
    service: str = Field(default="Commerce Insights API", description="Service identifier")
    version: str = Field(..., description="Application semantic version")
    environment: str = Field(..., description="Deployment environment")
    database: DatabaseHealth = Field(..., description="MongoDB connectivity details")
