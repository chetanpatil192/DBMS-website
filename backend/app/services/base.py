"""Base service interface and query instrumentation helpers."""

import time
from typing import Any, Dict, List, Optional, Tuple

from pymongo.database import Database

from app.core.logging import setup_logging

logger = setup_logging()


class BaseService:
    """Base class for domain and analytical services interacting with MongoDB."""

    def __init__(self, db: Database[Dict[str, Any]]) -> None:
        """Initializes service with an active MongoDB database instance."""
        self.db = db

    def measure_execution(
        self,
        operation_name: str,
        operation_callable: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, float]:
        """Executes a callable, measuring wall-clock duration in milliseconds.

        Args:
            operation_name: Descriptive label for log tracing.
            operation_callable: Function or method to execute.
            *args: Positional arguments for callable.
            **kwargs: Keyword arguments for callable.

        Returns:
            Tuple of (operation_result, duration_ms).
        """
        start = time.perf_counter()
        try:
            result = operation_callable(*args, **kwargs)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.debug("Operation '%s' completed in %.2f ms", operation_name, duration_ms)
            return result, duration_ms
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error("Operation '%s' failed after %.2f ms: %s", operation_name, duration_ms, exc)
            raise
