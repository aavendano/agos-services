"""
Tests for scoring engine and multi-criteria dimensions.
"""

import pytest
from analyzer.catalog import TechnologyCatalog
from analyzer.engine import (
    evaluate_technology,
    score_market_attractiveness,
    score_technology_maturity,
    score_defensibility_moat,
    score_gtm_velocity,
    score_risk_adjusted_viability,
)
from analyzer.models import InvestmentRecommendation


@pytest.fixture
def catalog():
    return TechnologyCatalog()


def test_catalog_loads_all_assets(catalog):
    assets = catalog.list_all()
    assert len(assets) >= 5
    ids = [a.id for a in assets]
    assert "agos-logic-solver" in ids
    assert "hi-bel-mcp-gateway" in ids
    assert "multi-agent-governance" in ids


def test_dimension_scoring_bounds(catalog):
    for asset in catalog.list_all():
        m_score = score_market_attractiveness(asset)
        t_score = score_technology_maturity(asset)
        moat_score = score_defensibility_moat(asset)
        gtm_score = score_gtm_velocity(asset)
        risk_score = score_risk_adjusted_viability(asset)

        assert 0.0 <= m_score <= 100.0
        assert 0.0 <= t_score <= 100.0
        assert 0.0 <= moat_score <= 100.0
        assert 0.0 <= gtm_score <= 100.0
        assert 0.0 <= risk_score <= 100.0


def test_evaluation_report_generation(catalog):
    asset = catalog.get_by_id("agos-logic-solver")
    assert asset is not None
    report = evaluate_technology(asset, run_simulations=False)
    
    assert report.composite_score > 0
    assert report.composite_score <= 100
    assert isinstance(report.recommendation, InvestmentRecommendation)
    assert len(report.strengths) > 0
    assert len(report.strategic_milestones) == 3
    assert report.financial_summary.five_year_revenue_usd > 0
