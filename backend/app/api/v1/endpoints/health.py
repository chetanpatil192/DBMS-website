"""Health check and diagnostic endpoint."""

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import Settings, get_settings
from app.db.client import db_manager
from app.schemas.common import DatabaseHealth, HealthCheckResponse, ResponseEnvelope, ResponseMeta

router = APIRouter(tags=["System Health"])


@router.get(
    "/health",
    response_model=ResponseEnvelope[HealthCheckResponse],
    summary="Service Health Check",
    description="Returns the operational status of the API server and connectivity to MongoDB.",
)
async def get_health(
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Executes a diagnostic ping against MongoDB and returns service state."""
    start_time = time.perf_counter()

    db_ping = db_manager.ping()
    is_db_connected = db_ping.get("connected", False)

    db_health = DatabaseHealth(
        connected=is_db_connected,
        latency_ms=db_ping.get("latency_ms", -1.0),
        database=db_ping.get("database"),
        error=db_ping.get("error"),
    )

    overall_status = "healthy" if is_db_connected else "degraded"
    http_status = status.HTTP_200_OK if is_db_connected else status.HTTP_503_SERVICE_UNAVAILABLE

    payload = HealthCheckResponse(
        status=overall_status,
        service=settings.PROJECT_NAME,
        version=__version__,
        environment=settings.ENVIRONMENT,
        database=db_health,
    )

    execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
    meta = ResponseMeta(execution_time_ms=execution_time_ms)

    response_data = ResponseEnvelope[HealthCheckResponse](
        data=payload,
        meta=meta,
    )

    return JSONResponse(
        status_code=http_status,
        content=response_data.model_dump(mode="json"),
    )
