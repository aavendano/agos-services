# Technology Commercial Potential Analyzer (`tech-eval`)

**Enterprise Multi-Criteria Commercialization & Financial Valuation Engine for Acquired & Proprietary Technologies.**

Part of the **AA Digital Business** governed services ecosystem (`agos-services`).

---

## 🎯 Overview

`tech-commercial-analyzer` is an enterprise software platform designed to evaluate, benchmark, and rank the commercial viability, financial unit economics, and go-to-market (GTM) velocity of technologies acquired or developed by the organization.

It provides both a high-throughput CLI tool (`tech-eval`) and an interactive Executive Web Dashboard backed by a FastAPI REST API.

---

## 🚀 Key Capabilities

1. **Multi-Dimensional Commercial Potential Scoring:**
   - **Market Attractiveness:** TAM / SAM / SOM modeling, CAGR, competitive density.
   - **Technology & Operational Maturity:** NASA/EU standard TRL (1-9), CRL (1-9), and technical debt index.
   - **Defensibility Moat:** Proprietary IP, switching costs, technical complexity, network effects.
   - **Financial Unit Economics:** CAC, LTV, LTV:CAC ratio, gross margin, capital payback period.
   - **GTM Velocity & Friction:** Sales cycle velocity, onboarding simplicity, customer market readiness.
   - **Risk-Adjusted Viability:** Regulatory hurdles, compliance feasibility, and architectural agility.

2. **5-Year Financial & DCF Engine:**
   - Net Present Value (NPV at 12% WACC)
   - 5-Year Revenue, COGS, OpEx, and Net Operating Profit projections
   - Break-even month and cumulative cash flow trajectories

3. **Probabilistic Monte Carlo Sensitivity Simulator:**
   - 1,000+ stochastic iterations sampling price elasticity, churn volatility, and CAC inflation
   - P10, P50 (median), and P90 confidence intervals for Revenue and NPV
   - Probability of profitability within 24 months

4. **Pre-Loaded Portfolio of AA Digital Business Technologies:**
   - `agos-logic-solver`: Deterministic architectural CSP solver & BOM engine (Score: 79.2 | BUY_INVEST)
   - `hi-bel-mcp-gateway`: Governed Shopify Model Context Protocol (MCP) gateway (Score: 85.4 | STRONG_BUY_SCALE)
   - `multi-agent-governance`: Autonomous multi-agent orchestration & budget platform (Score: 86.8 | STRONG_BUY_SCALE)
   - `codeium-language-server`: Local developer LSP daemon with Unleash feature engine (Score: 81.1 | STRONG_BUY_SCALE)
   - `kv-davinci-api`: Sub-millisecond state synchronization key-value engine (Score: 71.1 | BUY_INVEST)

---

## 🛠️ CLI Quickstart (`tech-eval`)

The executable binary is available in `$PATH` as `tech-eval`:

```bash
# 1. List all cataloged technologies with high-level metrics
tech-eval list

# 2. Deep-dive commercial evaluation for a specific asset
tech-eval analyze agos-logic-solver
tech-eval analyze hi-bel-mcp-gateway

# 3. View comparative portfolio ranking matrix
tech-eval compare

# 4. Export executive report to Markdown or JSON
tech-eval export --format markdown -o /tmp/portfolio_report.md
tech-eval export --format json -o /tmp/portfolio_report.json

# 5. Launch interactive web dashboard
tech-eval serve --port 8080
```

---

## 🌐 Web Dashboard & REST API

Run the web dashboard:
```bash
tech-eval serve --port 8080
```
Then open `http://localhost:8080` in your browser.

### REST Endpoints
- `GET /`: Interactive Web Dashboard
- `GET /api/health`: Service health check
- `GET /api/technologies`: List all technological asset manifests
- `GET /api/technologies/{id}`: Get detailed technology manifest
- `GET /api/evaluation/{id}`: Compute real-time commercial evaluation report
- `GET /api/portfolio-summary`: Aggregate portfolio metrics & comparative rankings
- `POST /api/custom-evaluate`: Test custom what-if scenarios dynamically

---

## Testing

From this directory (`services/tech-commercial-analyzer/`):

```bash
pytest
```

The service `pyproject.toml` sets `pythonpath = ["."]` so imports resolve without manual `PYTHONPATH`. Root `pytest` intentionally excludes this suite to avoid Django settings conflicts — see the monorepo [Testing section](../../README.md#6-run-test-suite) in the root README.
