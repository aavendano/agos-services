"""
Data models and schemas for Technology Commercial Potential Evaluation.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MonetizationType(str, Enum):
    B2B_SAAS = "b2b_saas"
    USAGE_BASED_API = "usage_based_api"
    ENTERPRISE_LICENSE = "enterprise_license"
    MARKETPLACE_COMMISSION = "marketplace_commission"
    HYBRID = "hybrid"


class InvestmentRecommendation(str, Enum):
    STRONG_BUY_SCALE = "STRONG_BUY_SCALE"          # High market potential, high moat, mature readiness (Score >= 80)
    BUY_INVEST = "BUY_INVEST"                      # Solid commercial viability, needs targeted R&D/GTM (Score 65-79)
    INCUBATE_VALIDATE = "INCUBATE_VALIDATE"        # Promising tech with unproven commercial traction (Score 50-64)
    MAINTAIN_HARVEST = "MAINTAIN_HARVEST"          # Niche profitability, limited scaling headroom (Score 40-49)
    PIVOT_REVISE = "PIVOT_REVISE"                  # Low moat, unfeasible unit economics or high regulatory risk (Score < 40)


class TechnologyReadiness(BaseModel):
    trl: int = Field(..., ge=1, le=9, description="Technology Readiness Level (1-9)")
    crl: int = Field(..., ge=1, le=9, description="Commercial Readiness Level (1-9)")
    operational_evidence: str = Field(..., description="Evidence of working system / test validation")
    tech_debt_score: float = Field(default=20.0, ge=0, le=100, description="Technical debt hurdle (0=clean, 100=crippling)")


class MarketSizing(BaseModel):
    tam_usd_m: float = Field(..., ge=0, description="Total Addressable Market in USD Millions")
    sam_usd_m: float = Field(..., ge=0, description="Serviceable Addressable Market in USD Millions")
    som_usd_m: float = Field(..., ge=0, description="Serviceable Obtainable Market in USD Millions (Year 3-5 target)")
    cagr_pct: float = Field(default=15.0, ge=0, le=100, description="Market Compound Annual Growth Rate (%)")
    target_segments: List[str] = Field(default_factory=list, description="Target customer ICP segments")
    competitive_density: str = Field(default="moderate", description="low, moderate, high, crowded")


class MonetizationUnitEconomics(BaseModel):
    pricing_type: MonetizationType = Field(default=MonetizationType.B2B_SAAS)
    avg_acv_usd: float = Field(..., ge=0, description="Average Annual Contract Value / Revenue per Customer (USD)")
    gross_margin_pct: float = Field(default=80.0, ge=0, le=100, description="Expected Gross Margin (%)")
    cac_usd: float = Field(default=5000.0, ge=0, description="Customer Acquisition Cost (USD)")
    monthly_churn_pct: float = Field(default=1.5, ge=0, le=100, description="Monthly churn rate (%)")
    target_year1_customers: int = Field(default=10, ge=1, description="Expected customer count year 1")
    customer_growth_rate_yoy_pct: float = Field(default=100.0, ge=0, description="YoY customer growth rate (%)")


class MoatAnalysis(BaseModel):
    proprietary_ip_score: float = Field(default=75.0, ge=0, le=100, description="Unique IP, algorithms, trade secrets (0-100)")
    switching_cost_score: float = Field(default=70.0, ge=0, le=100, description="Customer lock-in & workflow stickiness (0-100)")
    network_effects_score: float = Field(default=40.0, ge=0, le=100, description="Data / ecosystem network effects (0-100)")
    technical_complexity_score: float = Field(default=80.0, ge=0, le=100, description="Barrier to replicate by competitors (0-100)")


class GtmFriction(BaseModel):
    sales_cycle_days: int = Field(default=45, ge=1, description="Average sales cycle length in days")
    onboarding_effort_days: int = Field(default=7, ge=1, description="Days to onboard / integrate")
    market_awareness_score: float = Field(default=60.0, ge=0, le=100, description="Customer readiness/awareness (0=unknown, 100=ubiquitous)")
    regulatory_friction_score: float = Field(default=20.0, ge=0, le=100, description="Compliance & regulatory hurdle (0=none, 100=extreme)")


class TechAsset(BaseModel):
    id: str = Field(..., description="Unique technology identifier (e.g., agos-solver, hi-bel-mcp)")
    name: str = Field(..., description="Human-readable technology name")
    category: str = Field(..., description="Domain/category (e.g. AI Logic Engine, E-Commerce Infrastructure, Agent Ops)")
    repository_url: Optional[str] = None
    description: str = Field(..., description="Core description and technical capability")
    key_differentiators: List[str] = Field(default_factory=list)
    readiness: TechnologyReadiness
    market: MarketSizing
    unit_economics: MonetizationUnitEconomics
    moat: MoatAnalysis
    gtm: GtmFriction
    created_at: str = Field(default="2026-08-29T00:00:00Z")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class YearlyFinancial(BaseModel):
    year: int
    customers: int
    revenue_usd: float
    cogs_usd: float
    gross_profit_usd: float
    opex_usd: float
    net_operating_profit_usd: float
    cumulative_cashflow_usd: float


class FinancialProjection(BaseModel):
    discount_rate_pct: float = 12.0
    ltv_usd: float
    cac_usd: float
    ltv_to_cac_ratio: float
    payback_period_months: float
    five_year_revenue_usd: float
    five_year_npv_usd: float
    break_even_year: Optional[int] = None
    projections: List[YearlyFinancial]


class DimensionScores(BaseModel):
    market_attractiveness: float = Field(..., ge=0, le=100)
    technology_maturity: float = Field(..., ge=0, le=100)
    defensibility_moat: float = Field(..., ge=0, le=100)
    financial_unit_economics: float = Field(..., ge=0, le=100)
    gtm_velocity: float = Field(..., ge=0, le=100)
    risk_adjusted_viability: float = Field(..., ge=0, le=100)


class MonteCarloConfidence(BaseModel):
    runs: int
    p10_year3_revenue_usd: float
    p50_year3_revenue_usd: float
    p90_year3_revenue_usd: float
    p10_year5_npv_usd: float
    p50_year5_npv_usd: float
    p90_year5_npv_usd: float
    prob_profitable_month24_pct: float


class CommercialEvaluationReport(BaseModel):
    tech_id: str
    tech_name: str
    category: str
    composite_score: float = Field(..., ge=0, le=100)
    recommendation: InvestmentRecommendation
    dimension_scores: DimensionScores
    financial_summary: FinancialProjection
    monte_carlo: Optional[MonteCarloConfidence] = None
    strengths: List[str]
    weaknesses: List[str]
    strategic_milestones: List[str]
    suggested_pricing_strategy: str
