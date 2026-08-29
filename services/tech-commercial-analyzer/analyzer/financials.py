"""
Financial Modeling and Unit Economics Calculation Engine.
"""

from typing import List, Optional
from analyzer.models import TechAsset, FinancialProjection, YearlyFinancial


def calculate_annual_churn_rate(monthly_churn_pct: float) -> float:
    """Converts monthly churn percentage to compound annual churn rate (0.0 - 1.0)."""
    monthly_retention = 1.0 - (monthly_churn_pct / 100.0)
    annual_retention = max(0.0, monthly_retention ** 12)
    return max(0.01, 1.0 - annual_retention)


def compute_financial_projection(asset: TechAsset, discount_rate_pct: float = 12.0) -> FinancialProjection:
    """
    Computes full 5-year financial trajectory, unit economics, payback, and Net Present Value (NPV).
    """
    ue = asset.unit_economics
    annual_churn = calculate_annual_churn_rate(ue.monthly_churn_pct)
    gross_margin_factor = ue.gross_margin_pct / 100.0

    # LTV Calculation: (ACV * Gross Margin) / Annual Churn Rate
    annual_gross_profit_per_customer = ue.avg_acv_usd * gross_margin_factor
    ltv_usd = round(annual_gross_profit_per_customer / annual_churn, 2)
    cac_usd = round(ue.cac_usd, 2)
    
    ltv_to_cac = round(ltv_usd / cac_usd if cac_usd > 0 else 99.0, 2)
    
    # Payback Period (months): CAC / (ACV * Gross Margin / 12)
    monthly_gross_profit = (ue.avg_acv_usd * gross_margin_factor) / 12.0
    payback_months = round(cac_usd / monthly_gross_profit if monthly_gross_profit > 0 else 99.0, 1)

    # 5-Year Projection Simulation
    projections: List[YearlyFinancial] = []
    current_customers = float(ue.target_year1_customers)
    cumulative_cash = 0.0
    total_5yr_revenue = 0.0
    npv = 0.0
    break_even_year: Optional[int] = None

    discount_factor = 1.0 + (discount_rate_pct / 100.0)

    for year in range(1, 6):
        if year > 1:
            growth_factor = 1.0 + (ue.customer_growth_rate_yoy_pct / 100.0)
            # Decelerate growth progressively in later years (industry standard)
            deceleration = 1.0 - (0.12 * (year - 2))
            growth_factor = max(1.1, growth_factor * max(0.4, deceleration))
            new_acquired = current_customers * (growth_factor - 1.0)
            churned = current_customers * annual_churn
            current_customers = max(1.0, current_customers + new_acquired - churned)
        else:
            new_acquired = current_customers

        customer_count_int = int(round(current_customers))
        year_revenue = customer_count_int * ue.avg_acv_usd
        year_cogs = year_revenue * (1.0 - gross_margin_factor)
        gross_profit = year_revenue - year_cogs

        # OpEx: Sales & Marketing (CAC * new acquisitions) + R&D / G&A (baseline fixed + 15% revenue scaling)
        s_and_m_opex = new_acquired * cac_usd
        fixed_rd_ga = max(40000.0, 100000.0 + (year_revenue * 0.15))
        total_opex = s_and_m_opex + fixed_rd_ga

        net_operating_profit = gross_profit - total_opex
        cumulative_cash += net_operating_profit
        total_5yr_revenue += year_revenue

        discounted_cashflow = net_operating_profit / (discount_factor ** year)
        npv += discounted_cashflow

        if cumulative_cash >= 0 and break_even_year is None:
            break_even_year = year

        projections.append(YearlyFinancial(
            year=year,
            customers=customer_count_int,
            revenue_usd=round(year_revenue, 2),
            cogs_usd=round(year_cogs, 2),
            gross_profit_usd=round(gross_profit, 2),
            opex_usd=round(total_opex, 2),
            net_operating_profit_usd=round(net_operating_profit, 2),
            cumulative_cashflow_usd=round(cumulative_cash, 2)
        ))

    return FinancialProjection(
        discount_rate_pct=discount_rate_pct,
        ltv_usd=ltv_usd,
        cac_usd=cac_usd,
        ltv_to_cac_ratio=ltv_to_cac,
        payback_period_months=payback_months,
        five_year_revenue_usd=round(total_5yr_revenue, 2),
        five_year_npv_usd=round(npv, 2),
        break_even_year=break_even_year,
        projections=projections
    )
