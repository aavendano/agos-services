"""
Tests for Monte Carlo simulation engine.
"""

from analyzer.catalog import TechnologyCatalog
from analyzer.monte_carlo import run_monte_carlo_simulation


def test_monte_carlo_distribution():
    catalog = TechnologyCatalog()
    asset = catalog.get_by_id("agos-logic-solver")
    assert asset is not None

    mc = run_monte_carlo_simulation(asset, runs=100)
    assert mc.runs == 100
    assert mc.p10_year3_revenue_usd <= mc.p50_year3_revenue_usd <= mc.p90_year3_revenue_usd
    assert mc.p10_year5_npv_usd <= mc.p50_year5_npv_usd <= mc.p90_year5_npv_usd
    assert 0.0 <= mc.prob_profitable_month24_pct <= 100.0
