"""
Tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from analyzer.server import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_api_list_technologies():
    res = client.get("/api/technologies")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 5


def test_api_get_technology():
    res = client.get("/api/technologies/agos-logic-solver")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "agos-logic-solver"
    assert data["readiness"]["trl"] == 7


def test_api_get_evaluation():
    res = client.get("/api/evaluation/hi-bel-mcp-gateway?simulations=false")
    assert res.status_code == 200
    data = res.json()
    assert data["tech_id"] == "hi-bel-mcp-gateway"
    assert "composite_score" in data
    assert "dimension_scores" in data


def test_api_portfolio_summary():
    res = client.get("/api/portfolio-summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_assets"] >= 5
    assert data["portfolio_avg_score"] > 0
    assert len(data["rankings"]) >= 5


def test_dashboard_html_view():
    res = client.get("/")
    assert res.status_code == 200
    assert "AA Digital Business" in res.text
    assert "Technology Commercial Potential Analyzer" in res.text
