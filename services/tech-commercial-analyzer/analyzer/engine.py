"""
Core Multi-Criteria Technology Commercial Potential Scoring Engine.
"""

import math
from typing import List
from analyzer.models import (
    TechAsset,
    DimensionScores,
    CommercialEvaluationReport,
    InvestmentRecommendation,
)
from analyzer.financials import compute_financial_projection
from analyzer.monte_carlo import run_monte_carlo_simulation


def score_market_attractiveness(asset: TechAsset) -> float:
    """Scores addressable market scale, CAGR, and competitive space (0-100)."""
    # SAM sizing scale: $10M = 50pts, $100M = 75pts, $1B+ = 95pts
    sam = max(1.0, asset.market.sam_usd_m)
    size_score = min(100.0, 30.0 + (15.0 * math.log10(sam)))
    
    # Growth rate: 10% CAGR = 50pts, 30%+ CAGR = 100pts
    cagr_score = min(100.0, asset.market.cagr_pct * 3.33)

    # Competitive density penalty
    density_map = {"low": 95.0, "moderate": 75.0, "high": 50.0, "crowded": 30.0}
    comp_score = density_map.get(asset.market.competitive_density.lower(), 70.0)

    weighted = (size_score * 0.45) + (cagr_score * 0.35) + (comp_score * 0.20)
    return round(max(0.0, min(100.0, weighted)), 1)


def score_technology_maturity(asset: TechAsset) -> float:
    """Evaluates TRL, CRL, and technical debt penalty (0-100)."""
    # TRL 1-9 to 0-100
    trl_score = (asset.readiness.trl / 9.0) * 100.0
    # CRL 1-9 to 0-100
    crl_score = (asset.readiness.crl / 9.0) * 100.0
    
    # Tech debt penalty
    debt_penalty = asset.readiness.tech_debt_score * 0.30

    weighted = (trl_score * 0.50) + (crl_score * 0.50) - debt_penalty
    return round(max(0.0, min(100.0, weighted)), 1)


def score_defensibility_moat(asset: TechAsset) -> float:
    """Evaluates IP, switching costs, complexity, and network effects (0-100)."""
    m = asset.moat
    weighted = (
        (m.proprietary_ip_score * 0.35) +
        (m.switching_cost_score * 0.30) +
        (m.technical_complexity_score * 0.25) +
        (m.network_effects_score * 0.10)
    )
    return round(max(0.0, min(100.0, weighted)), 1)


def score_financial_unit_economics(projection) -> float:
    """Evaluates LTV:CAC, Gross Margin, and Payback Speed (0-100)."""
    # LTV:CAC score (>3 is 70pts, >5 is 90pts, >8 is 100pts)
    ratio = projection.ltv_to_cac_ratio
    if ratio >= 8.0:
        ltv_cac_score = 100.0
    elif ratio >= 5.0:
        ltv_cac_score = 85.0 + ((ratio - 5.0) * 5.0)
    elif ratio >= 3.0:
        ltv_cac_score = 70.0 + ((ratio - 3.0) * 7.5)
    elif ratio >= 1.5:
        ltv_cac_score = 40.0 + ((ratio - 1.5) * 20.0)
    else:
        ltv_cac_score = max(0.0, ratio * 25.0)

    # Payback period score (<6 mo = 100pts, <12 mo = 85pts, <18 mo = 65pts, >24 mo = 40pts)
    payback = projection.payback_period_months
    if payback <= 6.0:
        payback_score = 100.0
    elif payback <= 12.0:
        payback_score = 85.0 + ((12.0 - payback) * 2.5)
    elif payback <= 18.0:
        payback_score = 65.0 + ((18.0 - payback) * 3.3)
    elif payback <= 24.0:
        payback_score = 40.0 + ((24.0 - payback) * 4.1)
    else:
        payback_score = max(10.0, 40.0 - (payback - 24.0))

    # Net Margin & NPV positive
    npv_score = 100.0 if projection.five_year_npv_usd > 1_000_000 else (75.0 if projection.five_year_npv_usd > 0 else 30.0)

    weighted = (ltv_cac_score * 0.40) + (payback_score * 0.35) + (npv_score * 0.25)
    return round(max(0.0, min(100.0, weighted)), 1)


def score_gtm_velocity(asset: TechAsset) -> float:
    """Evaluates sales cycle velocity, onboarding simplicity, and market awareness (0-100)."""
    gtm = asset.gtm
    # Sales cycle: <= 14 days (100), 30 days (85), 60 days (65), 180 days (30)
    cycle = gtm.sales_cycle_days
    if cycle <= 14:
        cycle_score = 100.0
    elif cycle <= 30:
        cycle_score = 85.0 + ((30 - cycle) * 0.93)
    elif cycle <= 60:
        cycle_score = 65.0 + ((60 - cycle) * 0.66)
    else:
        cycle_score = max(15.0, 65.0 - ((cycle - 60) * 0.35))

    # Onboarding days: <= 2 days (100), <= 7 days (85), <= 30 days (50)
    onboard = gtm.onboarding_effort_days
    onboard_score = 100.0 if onboard <= 2 else (85.0 if onboard <= 7 else max(20.0, 85.0 - (onboard - 7) * 2.0))

    awareness_score = gtm.market_awareness_score

    weighted = (cycle_score * 0.40) + (onboard_score * 0.35) + (awareness_score * 0.25)
    return round(max(0.0, min(100.0, weighted)), 1)


def score_risk_adjusted_viability(asset: TechAsset) -> float:
    """Evaluates regulatory freedom, tech debt containment, and competitive safety (0-100)."""
    reg_freedom = 100.0 - asset.gtm.regulatory_friction_score
    clean_tech = 100.0 - asset.readiness.tech_debt_score
    weighted = (reg_freedom * 0.50) + (clean_tech * 0.50)
    return round(max(0.0, min(100.0, weighted)), 1)


def evaluate_technology(asset: TechAsset, run_simulations: bool = True) -> CommercialEvaluationReport:
    """
    Executes end-to-end commercial potential assessment for a given technology asset.
    """
    projection = compute_financial_projection(asset)
    
    market_score = score_market_attractiveness(asset)
    tech_score = score_technology_maturity(asset)
    moat_score = score_defensibility_moat(asset)
    fin_score = score_financial_unit_economics(projection)
    gtm_score = score_gtm_velocity(asset)
    risk_score = score_risk_adjusted_viability(asset)

    # Weighted Composite Score (Industry Gold Standard)
    # Market (25%) + Moat (20%) + Financials (20%) + Tech Readiness (15%) + GTM (10%) + Risk (10%)
    composite = (
        (market_score * 0.25) +
        (moat_score * 0.20) +
        (fin_score * 0.20) +
        (tech_score * 0.15) +
        (gtm_score * 0.10) +
        (risk_score * 0.10)
    )
    composite = round(max(0.0, min(100.0, composite)), 1)

    # Decision Matrix
    if composite >= 80.0:
        recommendation = InvestmentRecommendation.STRONG_BUY_SCALE
    elif composite >= 65.0:
        recommendation = InvestmentRecommendation.BUY_INVEST
    elif composite >= 50.0:
        recommendation = InvestmentRecommendation.INCUBATE_VALIDATE
    elif composite >= 40.0:
        recommendation = InvestmentRecommendation.MAINTAIN_HARVEST
    else:
        recommendation = InvestmentRecommendation.PIVOT_REVISE

    # Qualitative Strengths & Weaknesses derivation
    strengths: List[str] = []
    weaknesses: List[str] = []
    milestones: List[str] = []

    if market_score >= 75.0:
        strengths.append(f"Substantial market tailwinds in ${asset.market.sam_usd_m:.0f}M SAM with {asset.market.cagr_pct:.1f}% CAGR.")
    else:
        weaknesses.append("Target SAM or market expansion headroom is currently constrained.")

    if moat_score >= 75.0:
        strengths.append("High defensibility moat powered by proprietary IP and high switching costs.")
    elif moat_score < 55.0:
        weaknesses.append("Moderate competitive defensibility; vulnerable to commoditization.")

    if projection.ltv_to_cac_ratio >= 4.0:
        strengths.append(f"Highly accretive unit economics with {projection.ltv_to_cac_ratio:.1f}x LTV:CAC ratio.")
    else:
        weaknesses.append(f"LTV:CAC ratio ({projection.ltv_to_cac_ratio:.1f}x) requires CAC optimization or price tiering.")

    if projection.payback_period_months <= 12.0:
        strengths.append(f"Rapid capital recycling with {projection.payback_period_months:.1f} months payback.")
    else:
        weaknesses.append(f"Extended payback period ({projection.payback_period_months:.1f} mo) increases working capital requirements.")

    if asset.readiness.trl >= 7 and asset.readiness.crl >= 6:
        strengths.append(f"High technical and operational maturity (TRL {asset.readiness.trl} / CRL {asset.readiness.crl}).")
    else:
        weaknesses.append(f"Requires commercial pilot qualification (TRL {asset.readiness.trl}, CRL {asset.readiness.crl}).")

    # Strategic Next Milestones
    milestones.append(f"Phase 1: Secure initial {asset.unit_economics.target_year1_customers} reference customers across target ICP.")
    milestones.append(f"Phase 2: Formalize packaging for {asset.unit_economics.pricing_type.value} pricing and streamline onboarding under {asset.gtm.onboarding_effort_days} days.")
    milestones.append(f"Phase 3: Scale go-to-market distribution to capture target Year 3-5 SOM of ${asset.market.som_usd_m:.1f}M.")

    # Pricing strategy formulation
    pricing_strategy = (
        f"Implement a value-based {asset.unit_economics.pricing_type.value.upper().replace('_', ' ')} model "
        f"anchored at an average ACV of ${asset.unit_economics.avg_acv_usd:,.0f} with a target gross margin of "
        f"{asset.unit_economics.gross_margin_pct:.0f}%."
    )

    monte_carlo_res = run_monte_carlo_simulation(asset, runs=1000) if run_simulations else None

    return CommercialEvaluationReport(
        tech_id=asset.id,
        tech_name=asset.name,
        category=asset.category,
        composite_score=composite,
        recommendation=recommendation,
        dimension_scores=DimensionScores(
            market_attractiveness=market_score,
            technology_maturity=tech_score,
            defensibility_moat=moat_score,
            financial_unit_economics=fin_score,
            gtm_velocity=gtm_score,
            risk_adjusted_viability=risk_score
        ),
        financial_summary=projection,
        monte_carlo=monte_carlo_res,
        strengths=strengths,
        weaknesses=weaknesses,
        strategic_milestones=milestones,
        suggested_pricing_strategy=pricing_strategy
    )
