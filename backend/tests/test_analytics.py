"""Unit and contract tests for analytics dashboard endpoints."""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


def test_dashboard_endpoint(client: TestClient) -> None:
    """Tests that /api/v1/analytics/dashboard returns the expected envelope structure."""
    with patch("app.api.v1.endpoints.analytics.AnalyticsService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.get_dashboard_metrics.return_value = (
            {
                "total_customers": 5000,
                "total_orders": 44000,
                "total_revenue": 46242837.62,
                "average_order_value": 1264.29,
                "recent_orders": [
                    {
                        "order_id": "ord_00000001",
                        "customer_id": "cust_000001",
                        "customer_name": "Test Customer",
                        "customer_email": "test@example.com",
                        "region": "North America",
                        "order_date": "2026-10-15T10:00:00Z",
                        "status": "completed",
                        "payment_method": "credit_card",
                        "total_amount": 199.99,
                        "items_count": 2,
                    }
                ],
                "sales_trend": [
                    {
                        "period": "2026-05",
                        "revenue": 7500000.0,
                        "orders_count": 7000,
                    }
                ],
                "category_performance": [
                    {
                        "category": "Electronics",
                        "revenue": 9800000.0,
                        "orders_count": 18000,
                    }
                ],
            },
            12.5,  # db_duration_ms
            {"indexes_leveraged": ["idx_order_status_date"]},
        )

        response = client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 200
        payload = response.json()

        assert "data" in payload
        assert "meta" in payload
        data = payload["data"]
        assert data["total_customers"] == 5000
        assert data["total_orders"] == 44000
        assert data["total_revenue"] == 46242837.62
        assert len(data["recent_orders"]) == 1
        assert len(data["sales_trend"]) == 1
