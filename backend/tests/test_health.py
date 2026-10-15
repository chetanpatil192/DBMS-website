"""Unit tests for root status, health check, and error envelope formatting."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Verifies that the root discovery endpoint returns 200 with service information."""
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "Commerce Insights Test API"
    assert payload["status"] == "operational"
    assert "version" in payload
    assert payload["health_url"] == "/api/v1/health"


def test_health_endpoint_contract(client: TestClient) -> None:
    """Verifies that /api/v1/health conforms to the ResponseEnvelope structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()

    # Verify Envelope Fields
    assert "data" in payload
    assert "meta" in payload

    data = payload["data"]
    assert data["status"] in ("healthy", "degraded")
    assert data["service"] == "Commerce Insights Test API"
    assert "database" in data
    assert "connected" in data["database"]
    assert "latency_ms" in data["database"]

    meta = payload["meta"]
    assert "timestamp" in meta
    assert "execution_time_ms" in meta
    assert isinstance(meta["execution_time_ms"], (int, float))


def test_error_envelope_format_on_404(client: TestClient) -> None:
    """Verifies that non-existent routes return the standardized ErrorEnvelope format."""
    response = client.get("/api/v1/non-existent-resource-path")
    assert response.status_code == 404
    payload = response.json()

    # Must contain top-level 'error' key
    assert "error" in payload
    error = payload["error"]
    assert error["code"] == "ROUTE_NOT_FOUND"
    assert "message" in error
    assert "timestamp" in error
