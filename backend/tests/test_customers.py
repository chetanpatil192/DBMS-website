"""Unit and contract tests for customer listing and search endpoints."""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


def test_list_customers_endpoint(client: TestClient) -> None:
    """Tests that /api/v1/customers returns paginated customer items and metadata."""
    with patch("app.api.v1.endpoints.customers.CustomerService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.list_customers.return_value = (
            [
                {
                    "customer_id": "cust_000001",
                    "name": "Alice Smith",
                    "email": "alice@example.com",
                    "phone": "555-0100",
                    "city": "Seattle",
                    "country": "United States",
                    "region": "North America",
                    "total_spent": 1250.50,
                    "order_count": 5,
                    "created_at": "2026-01-15T08:00:00Z",
                }
            ],
            100,  # total items
            10,   # total pages
            4.2,  # db_duration_ms
            {"index_leveraged": "idx_cust_text_search"},
        )

        response = client.get("/api/v1/customers?page=1&page_size=10&search=Alice")
        assert response.status_code == 200
        payload = response.json()

        assert "data" in payload
        assert "meta" in payload
        assert len(payload["data"]) == 1
        assert payload["data"][0]["customer_id"] == "cust_000001"

        pagination = payload["meta"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
        assert pagination["total_items"] == 100
        assert pagination["total_pages"] == 10
