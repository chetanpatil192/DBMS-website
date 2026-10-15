"""Application-wide custom exceptions and centralized FastAPI exception handlers."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class CommerceInsightsException(Exception):
    """Base exception for all domain-specific Commerce Insights errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class DatabaseConnectionError(CommerceInsightsException):
    """Raised when the application fails to establish or maintain a MongoDB connection."""

    def __init__(
        self,
        message: str = "Unable to connect to the database service.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="DATABASE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class ResourceNotFoundError(CommerceInsightsException):
    """Raised when an analytical resource, dataset, or record is not found."""

    def __init__(
        self,
        resource_name: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        merged_details = {"resource": resource_name, "identifier": resource_id}
        if details:
            merged_details.update(details)
        super().__init__(
            message=f"{resource_name} with identifier '{resource_id}' was not found.",
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=merged_details,
        )


class ValidationException(CommerceInsightsException):
    """Raised when input parameters fail domain-level validation."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="INVALID_PARAMETERS",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


def _format_error_envelope(
    code: str,
    message: str,
    details: Any = None,
) -> Dict[str, Any]:
    """Formats an error response following the project's standard error envelope."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Registers standard exception handlers on the FastAPI application instance."""

    @app.exception_handler(CommerceInsightsException)
    async def handle_custom_exception(
        request: Request,
        exc: CommerceInsightsException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_format_error_envelope(
                code=exc.code,
                message=exc.message,
                details=exc.details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # Normalize validation errors into a clean dictionary
        formatted_errors = []
        for err in exc.errors():
            formatted_errors.append(
                {
                    "location": ".".join(str(loc) for loc in err.get("loc", [])),
                    "message": err.get("msg", ""),
                    "type": err.get("type", ""),
                }
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_format_error_envelope(
                code="SCHEMA_VALIDATION_ERROR",
                message="Incoming request payload or parameters failed validation.",
                details={"errors": formatted_errors},
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "ROUTE_NOT_FOUND"
        elif exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            code = "METHOD_NOT_ALLOWED"

        return JSONResponse(
            status_code=exc.status_code,
            content=_format_error_envelope(
                code=code,
                message=str(exc.detail),
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        # In production, avoid leaking internal exception details
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_format_error_envelope(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred. Please contact the administrator.",
                details={"exception_type": type(exc).__name__},
            ),
        )
