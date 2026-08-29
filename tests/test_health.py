import pytest
from django.test import Client

@pytest.mark.django_db
def test_health_check_endpoints():
    client = Client()
    for endpoint in ["/health/", "/healthz", "/healthz/", "/api/health", "/api/health/"]:
        res = client.get(endpoint)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["service"] == "hi-bel"
        assert data["mcp_gateway"] == "active"
        assert data["isolation_mode"] == "strict_mcp_only"
        assert data["checks"]["database"] == "ok"
        assert "redis" in data["checks"]
