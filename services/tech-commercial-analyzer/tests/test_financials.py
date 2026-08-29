"""
Tests for financial projections and unit economics engine.
"""

from analyzer.catalog import TechnologyCatalog
from analyzer.financials import compute_financial_projection, calculate_annual_churn_rate


def test_calculate_annual_churn_rate():
    # 1.5% monthly churn -> ~16.6% annual churn
    annual = calculate_annual_churn_rate(1.5)
    assert 0.15 <= annual <= 0.18

    # Zero/low churn edge cases
    annual_low = calculate_annual_churn_rate(0.1)
    assert annual_low > 0.0


def test_compute_financial_projection():
    catalog = TechnologyCatalog()
    asset = catalog.get_by_id("hi-bel-mcp-gateway")
    assert asset is not None

    proj = compute_financial_projection(asset, discount_rate_pct=12.0)
    assert proj.ltv_usd > proj.cac_usd
    assert proj.ltv_to_cac_ratio > 3.0
    assert proj.payback_period_months < 12.0
    assert len(proj.projections) == 5
    assert proj.projections[0].year == 1
    assert proj.projections[4].year == 5
    assert proj.five_year_revenue_usd > 1_000_000.0
    assert proj.five_year_npv_usd > 0.0
