"""
Probabilistic Monte Carlo Simulation Engine for Technology Investment Analysis.
"""

import random
import math
from typing import List
from analyzer.models import TechAsset, MonteCarloConfidence
from analyzer.financials import compute_financial_projection, calculate_annual_churn_rate


def run_monte_carlo_simulation(asset: TechAsset, runs: int = 1000) -> MonteCarloConfidence:
    """
    Runs probabilistic sensitivity simulations across customer acquisition, pricing elasticity,
    churn variations, and CAC volatility.
    """
    year3_revenues: List[float] = []
    year5_npvs: List[float] = []
    profitable_by_month24_count = 0

    base_acv = asset.unit_economics.avg_acv_usd
    base_cac = asset.unit_economics.cac_usd
    base_churn = asset.unit_economics.monthly_churn_pct
    base_growth = asset.unit_economics.customer_growth_rate_yoy_pct

    for _ in range(runs):
        # Sample stochastic parameters
        sampled_acv = max(base_acv * 0.5, random.gauss(base_acv, base_acv * 0.15))
        sampled_cac = max(base_cac * 0.5, random.gauss(base_cac, base_cac * 0.20))
        sampled_churn = max(0.2, random.gauss(base_churn, base_churn * 0.25))
        sampled_growth = max(10.0, random.gauss(base_growth, base_growth * 0.30))

        sim_asset = asset.model_copy(deep=True)
        sim_asset.unit_economics.avg_acv_usd = sampled_acv
        sim_asset.unit_economics.cac_usd = sampled_cac
        sim_asset.unit_economics.monthly_churn_pct = sampled_churn
        sim_asset.unit_economics.customer_growth_rate_yoy_pct = sampled_growth

        projection = compute_financial_projection(sim_asset)
        
        # Collect metric points
        if len(projection.projections) >= 3:
            year3_revenues.append(projection.projections[2].revenue_usd)
        else:
            year3_revenues.append(0.0)

        year5_npvs.append(projection.five_year_npv_usd)

        # Check Month 24 profitability (Cumulative cashflow by Year 2)
        if len(projection.projections) >= 2 and projection.projections[1].cumulative_cashflow_usd > 0:
            profitable_by_month24_count += 1

    year3_revenues.sort()
    year5_npvs.sort()

    def get_percentile(sorted_list: List[float], pct: float) -> float:
        idx = int(len(sorted_list) * (pct / 100.0))
        idx = min(max(0, idx), len(sorted_list) - 1)
        return round(sorted_list[idx], 2)

    return MonteCarloConfidence(
        runs=runs,
        p10_year3_revenue_usd=get_percentile(year3_revenues, 10),
        p50_year3_revenue_usd=get_percentile(year3_revenues, 50),
        p90_year3_revenue_usd=get_percentile(year3_revenues, 90),
        p10_year5_npv_usd=get_percentile(year5_npvs, 10),
        p50_year5_npv_usd=get_percentile(year5_npvs, 50),
        p90_year5_npv_usd=get_percentile(year5_npvs, 90),
        prob_profitable_month24_pct=round((profitable_by_month24_count / runs) * 100.0, 1)
    )
