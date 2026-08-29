"""
Command-Line Interface (CLI) for Tech Commercial Potential Evaluator.
"""

import sys
import os
import argparse
import json
from typing import List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from analyzer.catalog import TechnologyCatalog
from analyzer.engine import evaluate_technology
from analyzer.financials import compute_financial_projection
from analyzer.models import TechAsset, InvestmentRecommendation

console = Console()


def cmd_list(catalog: TechnologyCatalog, args):
    """Lists all cataloged technologies with high-level readiness and market metrics."""
    assets = catalog.list_all()
    if not assets:
        console.print("[yellow]No technologies found in catalog.[/yellow]")
        return

    table = Table(title="🏢 AA Digital Business — Cataloged Technology Portfolio", box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Technology Name", style="bold white")
    table.add_column("Category", style="magenta")
    table.add_column("TRL/CRL", justify="center", style="green")
    table.add_column("SAM ($M)", justify="right", style="yellow")
    table.add_column("Pricing", style="blue")
    table.add_column("Avg ACV", justify="right", style="green")

    for a in assets:
        table.add_row(
            a.id,
            a.name,
            a.category,
            f"TRL {a.readiness.trl} / CRL {a.readiness.crl}",
            f"${a.market.sam_usd_m:.0f}M",
            a.unit_economics.pricing_type.value,
            f"${a.unit_economics.avg_acv_usd:,.0f}"
        )

    console.print(table)
    console.print(f"[dim]Total indexed assets: {len(assets)} | Run 'tech-eval analyze <id>' for full report.[/dim]\n")


def cmd_analyze(catalog: TechnologyCatalog, args):
    """Runs a deep commercial evaluation for a specific technology asset."""
    tech_id = args.tech_id
    asset = catalog.get_by_id(tech_id)
    if not asset:
        console.print(f"[red]Error: Technology '{tech_id}' not found in catalog.[/red]")
        sys.exit(1)

    console.print(f"\n[bold green]⚙️  Evaluating Commercial Potential for '{asset.name}'...[/bold green]\n")
    report = evaluate_technology(asset, run_simulations=True)

    # Color badge for recommendation
    rec_colors = {
        InvestmentRecommendation.STRONG_BUY_SCALE: "bold white on green",
        InvestmentRecommendation.BUY_INVEST: "bold black on bright_green",
        InvestmentRecommendation.INCUBATE_VALIDATE: "bold black on yellow",
        InvestmentRecommendation.MAINTAIN_HARVEST: "bold white on blue",
        InvestmentRecommendation.PIVOT_REVISE: "bold white on red",
    }
    badge_style = rec_colors.get(report.recommendation, "bold white on cyan")

    # Header Panel
    header_text = (
        f"[bold]{asset.name}[/bold] ({asset.category})\n"
        f"[dim]{asset.description}[/dim]\n\n"
        f"🏆 [bold]Composite Commercial Score:[/bold] [bold cyan]{report.composite_score:.1f} / 100[/bold cyan]\n"
        f"🎯 [bold]Investment Recommendation:[/bold] [{badge_style}] {report.recommendation.value} [/{badge_style}]"
    )
    console.print(Panel(header_text, title="Executive Assessment", border_style="cyan"))

    # Dimension Scores Table
    dim_table = Table(title="📊 Multi-Dimensional Commercial Evaluation Breakdown", box=box.SIMPLE_HEAVY)
    dim_table.add_column("Dimension", style="bold white")
    dim_table.add_column("Score (0-100)", justify="right", style="cyan")
    dim_table.add_column("Key Strategic Drivers", style="dim")

    dim_table.add_row(
        "Market Attractiveness",
        f"{report.dimension_scores.market_attractiveness:.1f}",
        f"TAM ${asset.market.tam_usd_m:.0f}M | SAM ${asset.market.sam_usd_m:.0f}M | {asset.market.cagr_pct:.1f}% CAGR"
    )
    dim_table.add_row(
        "Technology & Operational Maturity",
        f"{report.dimension_scores.technology_maturity:.1f}",
        f"TRL {asset.readiness.trl}/9 | CRL {asset.readiness.crl}/9 | Tech Debt: {asset.readiness.tech_debt_score:.0f}%"
    )
    dim_table.add_row(
        "Defensibility & IP Moat",
        f"{report.dimension_scores.defensibility_moat:.1f}",
        f"IP: {asset.moat.proprietary_ip_score:.0f} | Switching Cost: {asset.moat.switching_cost_score:.0f} | Complexity: {asset.moat.technical_complexity_score:.0f}"
    )
    dim_table.add_row(
        "Financial & Unit Economics",
        f"{report.dimension_scores.financial_unit_economics:.1f}",
        f"LTV:CAC {report.financial_summary.ltv_to_cac_ratio:.1f}x | Payback: {report.financial_summary.payback_period_months:.1f} mo | Gross Margin: {asset.unit_economics.gross_margin_pct:.0f}%"
    )
    dim_table.add_row(
        "GTM Velocity & Adoption",
        f"{report.dimension_scores.gtm_velocity:.1f}",
        f"Sales Cycle: {asset.gtm.sales_cycle_days}d | Onboarding: {asset.gtm.onboarding_effort_days}d | Awareness: {asset.gtm.market_awareness_score:.0f}"
    )
    dim_table.add_row(
        "Risk-Adjusted Viability",
        f"{report.dimension_scores.risk_adjusted_viability:.1f}",
        f"Regulatory Friction: {asset.gtm.regulatory_friction_score:.0f}% | Freedom to Operate: High"
    )
    console.print(dim_table)

    # 5-Year Financial Projection Table
    fin_table = Table(title="📈 5-Year Financial & Unit Economics Trajectory", box=box.ROUNDED)
    fin_table.add_column("Year", justify="center", style="bold")
    fin_table.add_column("Active Customers", justify="right", style="cyan")
    fin_table.add_column("Annual Revenue", justify="right", style="green")
    fin_table.add_column("Gross Profit", justify="right", style="yellow")
    fin_table.add_column("Total OpEx", justify="right", style="red")
    fin_table.add_column("Net Op Profit", justify="right", style="bold green")
    fin_table.add_column("Cumulative Cash", justify="right", style="magenta")

    for p in report.financial_summary.projections:
        net_style = "bold green" if p.net_operating_profit_usd >= 0 else "red"
        fin_table.add_row(
            f"Y{p.year}",
            f"{p.customers}",
            f"${p.revenue_usd:,.0f}",
            f"${p.gross_profit_usd:,.0f}",
            f"${p.opex_usd:,.0f}",
            f"[{net_style}]${p.net_operating_profit_usd:,.0f}[/{net_style}]",
            f"${p.cumulative_cashflow_usd:,.0f}"
        )
    console.print(fin_table)

    # Financial Summary Metrics
    console.print(
        f"[bold]5-Year NPV (12% WACC):[/bold] [green]${report.financial_summary.five_year_npv_usd:,.0f}[/green] | "
        f"[bold]LTV:[/bold] [cyan]${report.financial_summary.ltv_usd:,.0f}[/cyan] | "
        f"[bold]CAC:[/bold] [yellow]${report.financial_summary.cac_usd:,.0f}[/yellow] | "
        f"[bold]Break-even:[/bold] [magenta]Year {report.financial_summary.break_even_year or 'N/A'}[/magenta]\n"
    )

    # Monte Carlo Summary
    if report.monte_carlo:
        mc = report.monte_carlo
        mc_text = (
            f"🎲 [bold]Monte Carlo Simulation ({mc.runs:,} iterations):[/bold]\n"
            f" • [bold]Year 3 Revenue Confidence:[/bold] P10: ${mc.p10_year3_revenue_usd:,.0f} | [green]P50 (Median): ${mc.p50_year3_revenue_usd:,.0f}[/green] | P90: ${mc.p90_year3_revenue_usd:,.0f}\n"
            f" • [bold]5-Year NPV Distribution:[/bold] P10: ${mc.p10_year5_npv_usd:,.0f} | [green]P50 (Median): ${mc.p50_year5_npv_usd:,.0f}[/green] | P90: ${mc.p90_year5_npv_usd:,.0f}\n"
            f" • [bold]Probability of Positive Cashflow by Month 24:[/bold] [bold cyan]{mc.prob_profitable_month24_pct}%[/bold cyan]"
        )
        console.print(Panel(mc_text, title="Stochastic Risk & Sensitivity Analysis", border_style="yellow"))

    # Strengths & Next Steps
    col1 = "\n".join([f"✅ {s}" for s in report.strengths])
    col2 = "\n".join([f"⚠️ {w}" for w in report.weaknesses])
    console.print(Panel(f"[bold green]Competitive Strengths:[/bold green]\n{col1}\n\n[bold red]Vulnerabilities / Attention Areas:[/bold red]\n{col2}", title="Strategic SWOT", border_style="blue"))

    milestones_str = "\n".join([f"{idx+1}. {m}" for idx, m in enumerate(report.strategic_milestones)])
    console.print(Panel(f"[bold white]Recommended Execution Milestones:[/bold white]\n{milestones_str}\n\n[bold cyan]Packaging & Pricing Strategy:[/bold cyan]\n{report.suggested_pricing_strategy}", title="Commercial Execution Plan", border_style="green"))


def cmd_compare(catalog: TechnologyCatalog, args):
    """Generates comparative ranking and portfolio matrix across all technologies."""
    assets = catalog.list_all()
    if not assets:
        console.print("[yellow]No technologies in catalog.[/yellow]")
        return

    reports = [evaluate_technology(a, run_simulations=False) for a in assets]
    reports.sort(key=lambda r: r.composite_score, reverse=True)

    table = Table(title="🏆 Organization Technology Commercial Portfolio Ranking", box=box.ROUNDED)
    table.add_column("Rank", justify="center", style="bold")
    table.add_column("Technology", style="bold white")
    table.add_column("Score", justify="right", style="bold cyan")
    table.add_column("Recommendation", style="bold magenta")
    table.add_column("Market", justify="right", style="yellow")
    table.add_column("Moat", justify="right", style="cyan")
    table.add_column("LTV:CAC", justify="right", style="green")
    table.add_column("5-Yr NPV", justify="right", style="green")
    table.add_column("Payback", justify="right", style="blue")

    for rank, r in enumerate(reports, 1):
        table.add_row(
            f"#{rank}",
            f"{r.tech_name}",
            f"{r.composite_score:.1f}",
            r.recommendation.value,
            f"{r.dimension_scores.market_attractiveness:.0f}",
            f"{r.dimension_scores.defensibility_moat:.0f}",
            f"{r.financial_summary.ltv_to_cac_ratio:.1f}x",
            f"${r.financial_summary.five_year_npv_usd:,.0f}",
            f"{r.financial_summary.payback_period_months:.1f} mo"
        )

    console.print(table)


def cmd_export(catalog: TechnologyCatalog, args):
    """Exports portfolio analysis to Markdown, JSON, or HTML file."""
    format_type = args.format.lower()
    output_path = args.output
    assets = catalog.list_all()
    reports = [evaluate_technology(a, run_simulations=True) for a in assets]
    reports.sort(key=lambda r: r.composite_score, reverse=True)

    if format_type == "json":
        data = [r.model_dump() for r in reports]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        console.print(f"[green]Exported JSON report to {output_path}[/green]")

    elif format_type in ["markdown", "md"]:
        md_lines = [
            "# AA Digital Business — Commercial Potential Portfolio Assessment",
            f"**Date:** 2026-08-29 | **Total Technologies Evaluated:** {len(reports)}",
            "",
            "## Executive Summary & Portfolio Ranking",
            "",
            "| Rank | Technology | Composite Score | Recommendation | 5-Yr NPV | LTV:CAC | Payback |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for idx, r in enumerate(reports, 1):
            md_lines.append(
                f"| #{idx} | **{r.tech_name}** | `{r.composite_score:.1f}/100` | `{r.recommendation.value}` | ${r.financial_summary.five_year_npv_usd:,.0f} | {r.financial_summary.ltv_to_cac_ratio:.1f}x | {r.financial_summary.payback_period_months:.1f} mo |"
            )

        md_lines.append("\n---\n")
        for r in reports:
            asset = next(a for a in assets if a.id == r.tech_id)
            md_lines.extend([
                f"### {r.tech_name} (`{r.tech_id}`)",
                f"- **Category:** {r.category}",
                f"- **Description:** {asset.description}",
                f"- **Composite Score:** **{r.composite_score:.1f} / 100** ({r.recommendation.value})",
                f"- **Market:** TAM ${asset.market.tam_usd_m:.0f}M | SAM ${asset.market.sam_usd_m:.0f}M | {asset.market.cagr_pct:.1f}% CAGR",
                f"- **Readiness:** TRL {asset.readiness.trl}/9 | CRL {asset.readiness.crl}/9",
                f"- **Unit Economics:** ACV ${asset.unit_economics.avg_acv_usd:,.0f} | Margin {asset.unit_economics.gross_margin_pct:.0f}% | LTV:CAC {r.financial_summary.ltv_to_cac_ratio:.1f}x",
                "",
                "#### Strengths",
                *[f"- {s}" for s in r.strengths],
                "",
                "#### Strategic Execution Milestones",
                *[f"1. {m}" for m in r.strategic_milestones],
                "",
                "---"
            ])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        console.print(f"[green]Exported Markdown report to {output_path}[/green]")


def cmd_serve(catalog: TechnologyCatalog, args):
    """Launches the interactive web dashboard server."""
    import uvicorn
    from analyzer.server import app
    port = args.port or 8080
    host = args.host or "0.0.0.0"
    console.print(f"[bold green]🚀 Launching Tech Commercial Analyzer Web Dashboard on http://{host}:{port}...[/bold green]")
    uvicorn.run(app, host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="AA Digital Business — Technology Commercial Potential Evaluator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    p_list = subparsers.add_parser("list", help="List all cataloged technology assets")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Deep commercial analysis of a specific technology")
    p_analyze.add_argument("tech_id", help="Technology asset ID (e.g. agos-logic-solver, hi-bel-mcp-gateway)")

    # compare
    p_compare = subparsers.add_parser("compare", help="Comparative portfolio ranking matrix")

    # export
    p_export = subparsers.add_parser("export", help="Export report to file")
    p_export.add_argument("--format", choices=["json", "markdown", "md"], default="markdown", help="Output format")
    p_export.add_argument("--output", "-o", default="commercial_evaluation_report.md", help="Target output filepath")

    # serve
    p_serve = subparsers.add_parser("serve", help="Start the interactive Web Dashboard")
    p_serve.add_argument("--port", "-p", type=int, default=8080, help="Web server port")
    p_serve.add_argument("--host", default="0.0.0.0", help="Web server host")

    args = parser.parse_args()
    catalog = TechnologyCatalog()

    if args.command == "list":
        cmd_list(catalog, args)
    elif args.command == "analyze":
        cmd_analyze(catalog, args)
    elif args.command == "compare":
        cmd_compare(catalog, args)
    elif args.command == "export":
        cmd_export(catalog, args)
    elif args.command == "serve":
        cmd_serve(catalog, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
