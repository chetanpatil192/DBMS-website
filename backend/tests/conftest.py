"""Shared pytest fixtures and test environment configuration."""

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provides isolated settings configured for the test environment."""
    return Settings(
        PROJECT_NAME="Commerce Insights Test API",
        ENVIRONMENT="testing",
        DEBUG=True,
        API_V1_STR="/api/v1",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB_NAME="commerce_insights_test",
        MONGODB_MIN_POOL_SIZE=1,
        MONGODB_MAX_POOL_SIZE=5,
        MONGODB_TIMEOUT_MS=1000,
    )


@pytest.fixture
def client(test_settings: Settings) -> Generator[TestClient, None, None]:
    """Provides a synchronous FastAPI TestClient with mocked database lifespan."""
    from app.db.client import get_db
    app = create_app(settings=test_settings)
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_db] = lambda: MagicMock()

    # Mock MongoDB connection during testing to avoid external network dependencies
    with patch("app.main.db_manager") as mock_db_mgr, \
         patch("app.api.v1.endpoints.health.db_manager") as mock_health_db_mgr:
        mock_response = {
            "connected": True,
            "latency_ms": 1.5,
            "database": "commerce_insights_test",
        }
        mock_db_mgr.ping.return_value = mock_response
        mock_health_db_mgr.ping.return_value = mock_response
        with TestClient(app) as test_client:
            yield test_client
