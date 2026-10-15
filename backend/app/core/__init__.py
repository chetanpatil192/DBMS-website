"""Core module for configuration, logging, and error handling."""

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    CommerceInsightsException,
    DatabaseConnectionError,
    ResourceNotFoundError,
    ValidationException,
    register_exception_handlers,
)
from app.core.logging import setup_logging

__all__ = [
    "Settings",
    "get_settings",
    "setup_logging",
    "CommerceInsightsException",
    "DatabaseConnectionError",
    "ResourceNotFoundError",
    "ValidationException",
    "register_exception_handlers",
]
