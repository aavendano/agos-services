"""
FastAPI Server and Web Dashboard for Technology Commercial Potential Evaluator.
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from analyzer.models import TechAsset, CommercialEvaluationReport
from analyzer.catalog import TechnologyCatalog
from analyzer.engine import evaluate_technology

app = FastAPI(
    title="AA Digital Business — Tech Commercial Potential Analyzer",
    description="Enterprise analyzer for evaluating commercial viability, unit economics, TRL/CRL, and GTM potential.",
    version="1.0.0"
)

catalog = TechnologyCatalog()
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=template_dir)


@app.get("/", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    """Renders the single-page executive web dashboard."""
    assets = catalog.list_all()
    reports = [evaluate_technology(a, run_simulations=True) for a in assets]
    reports.sort(key=lambda r: r.composite_score, reverse=True)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "assets": [a.model_dump() for a in assets],
            "reports": [r.model_dump() for r in reports]
        }
    )


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "tech-commercial-analyzer", "version": "1.0.0"}


@app.get("/api/technologies", response_model=List[TechAsset])
async def list_technologies():
    """Lists all cataloged technological assets."""
    return catalog.list_all()


@app.get("/api/technologies/{tech_id}", response_model=TechAsset)
async def get_technology(tech_id: str):
    """Retrieves a technology asset by ID."""
    asset = catalog.get_by_id(tech_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Technology asset not found")
    return asset


@app.post("/api/technologies", response_model=TechAsset)
async def create_technology(asset: TechAsset):
    """Registers a new technology asset in the catalog."""
    catalog.save_asset(asset)
    return asset


@app.get("/api/evaluation/{tech_id}", response_model=CommercialEvaluationReport)
async def get_evaluation(tech_id: str, simulations: bool = True):
    """Computes real-time commercial potential evaluation for a given technology."""
    asset = catalog.get_by_id(tech_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Technology asset not found")
    return evaluate_technology(asset, run_simulations=simulations)


@app.get("/api/portfolio-summary")
async def get_portfolio_summary():
    """Returns comparative ranking and summary metrics for all cataloged assets."""
    assets = catalog.list_all()
    reports = [evaluate_technology(a, run_simulations=False) for a in assets]
    reports.sort(key=lambda r: r.composite_score, reverse=True)
    
    total_som = sum(a.market.som_usd_m for a in assets)
    total_5yr_npv = sum(r.financial_summary.five_year_npv_usd for r in reports)
    avg_score = sum(r.composite_score for r in reports) / len(reports) if reports else 0.0

    return {
        "total_assets": len(assets),
        "portfolio_avg_score": round(avg_score, 1),
        "portfolio_total_som_usd_m": round(total_som, 1),
        "portfolio_total_5yr_npv_usd": round(total_5yr_npv, 2),
        "rankings": [
            {
                "rank": idx + 1,
                "id": r.tech_id,
                "name": r.tech_name,
                "category": r.category,
                "composite_score": r.composite_score,
                "recommendation": r.recommendation.value,
                "five_year_npv_usd": r.financial_summary.five_year_npv_usd,
                "ltv_to_cac": r.financial_summary.ltv_to_cac_ratio,
                "payback_months": r.financial_summary.payback_period_months
            }
            for idx, r in enumerate(reports)
        ]
    }


@app.post("/api/custom-evaluate", response_model=CommercialEvaluationReport)
async def evaluate_custom(asset: TechAsset, simulations: bool = True):
    """Evaluates arbitrary custom parameters without saving to catalog."""
    return evaluate_technology(asset, run_simulations=simulations)
