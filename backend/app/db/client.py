"""MongoDB client lifecycle management and connection pooling."""

import time
from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import Settings, get_settings
from app.core.exceptions import DatabaseConnectionError
from app.core.logging import setup_logging

logger = setup_logging()


class MongoDBManager:
    """Manages the lifecycle, pooling, and health checks of the PyMongo client."""

    def __init__(self) -> None:
        self._client: Optional[MongoClient[Dict[str, Any]]] = None
        self._settings: Optional[Settings] = None

    @property
    def is_connected(self) -> bool:
        """Indicates whether a client instance has been initialized."""
        return self._client is not None

    def connect(self, settings: Optional[Settings] = None) -> None:
        """Initializes the PyMongo client with connection pooling configuration.

        Args:
            settings: Optional explicit settings instance; defaults to cached get_settings().
        """
        self._settings = settings or get_settings()

        logger.info(
            "Initializing PyMongo client (URI: %s, Database: %s, MinPool: %d, MaxPool: %d)",
            self._settings.MONGODB_URI,
            self._settings.MONGODB_DB_NAME,
            self._settings.MONGODB_MIN_POOL_SIZE,
            self._settings.MONGODB_MAX_POOL_SIZE,
        )

        try:
            self._client = MongoClient(
                self._settings.MONGODB_URI,
                minPoolSize=self._settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=self._settings.MONGODB_MAX_POOL_SIZE,
                serverSelectionTimeoutMS=self._settings.MONGODB_TIMEOUT_MS,
                connectTimeoutMS=self._settings.MONGODB_TIMEOUT_MS,
                socketTimeoutMS=30000,
                retryWrites=True,
                retryReads=True,
                appname="CommerceInsightsBackend",
            )
        except Exception as exc:
            logger.error("Failed to initialize PyMongo client: %s", exc)
            self._client = None
            raise DatabaseConnectionError(
                message=f"Failed to initialize database client: {exc}",
                details={"uri": self._settings.MONGODB_URI},
            ) from exc

    def close(self) -> None:
        """Closes all open sockets in the PyMongo connection pool cleanly."""
        if self._client:
            logger.info("Closing PyMongo connection pool...")
            self._client.close()
            self._client = None
            logger.info("PyMongo connection pool closed.")

    def get_client(self) -> MongoClient[Dict[str, Any]]:
        """Returns the active PyMongo client.

        Raises:
            DatabaseConnectionError: If client is not initialized.
        """
        if self._client is None:
            raise DatabaseConnectionError("Database client is not connected.")
        return self._client

    def get_database(self, db_name: Optional[str] = None) -> Database[Dict[str, Any]]:
        """Returns the target MongoDB database instance.

        Args:
            db_name: Target database name. Defaults to configured MONGODB_DB_NAME.
        """
        client = self.get_client()
        target_name = db_name or (self._settings.MONGODB_DB_NAME if self._settings else "commerce_insights")
        return client[target_name]

    def ping(self) -> Dict[str, Any]:
        """Pings the MongoDB instance and records round-trip latency in milliseconds.

        Returns:
            Dictionary with status, latency_ms, and database name.
        """
        if self._client is None:
            return {
                "connected": False,
                "latency_ms": -1.0,
                "error": "Client not initialized",
            }

        start_time = time.perf_counter()
        try:
            # Issue lightweight ping command to admin database
            self._client.admin.command("ping")
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "connected": True,
                "latency_ms": latency_ms,
                "database": self._settings.MONGODB_DB_NAME if self._settings else "commerce_insights",
            }
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning("MongoDB ping failed: %s", exc)
            return {
                "connected": False,
                "latency_ms": latency_ms,
                "error": str(exc),
            }


# Global database manager singleton
db_manager = MongoDBManager()


def get_db() -> Database[Dict[str, Any]]:
    """FastAPI dependency provider for database instance."""
    return db_manager.get_database()


def get_mongo_client() -> MongoClient[Dict[str, Any]]:
    """FastAPI dependency provider for raw MongoClient instance."""
    return db_manager.get_client()
