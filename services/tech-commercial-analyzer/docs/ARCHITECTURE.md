# Architecture Specification (STD-DOC-001)

**Service:** `tech-commercial-analyzer`  
**Standard:** STD-DOC-001  
**Author:** CEO (`05c05fac-bda2-48ae-8284-ebed265cc4dc`)  
**Status:** Approved & Verified  

---

## 1. System Overview

`tech-commercial-analyzer` follows a modular, clean-architecture pattern separating domain models, scoring algorithms, financial projection engines, stochastic simulators, and presentation layers (CLI + REST + Web).

```
┌────────────────────────────────────────────────────────┐
│                   Presentation Layer                   │
│   ┌─────────────────────────┐ ┌──────────────────────┐ │
│   │ Rich Terminal CLI Tool  │ │  FastAPI Web Server  │ │
│   │       (tech-eval)       │ │     & Dashboard      │ │
│   └────────────┬────────────┘ └──────────┬───────────┘ │
└────────────────┼─────────────────────────┼─────────────┘
                 │                         │
┌────────────────▼─────────────────────────▼─────────────┐
│                      Core Engine                       │
│   ┌─────────────────────────┐ ┌──────────────────────┐ │
│   │ Multi-Criteria Scoring  │ │ Financial Projections│ │
│   │    (analyzer/engine)    │ │ (analyzer/financials)│ │
│   └────────────┬────────────┘ └──────────┬───────────┘ │
│                │                         │             │
│   ┌────────────▼────────────┐ ┌──────────▼───────────┐ │
│   │  Monte Carlo Simulator  │ │  Catalog Repository  │ │
│   │ (analyzer/monte_carlo)  │ │  (analyzer/catalog)  │ │
│   └─────────────────────────┘ └──────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## 2. Mathematical Scoring Framework

The Composite Commercial Score ($S_{comp} \in [0, 100]$) is computed as a weighted sum of 6 core pillars:

$$S_{comp} = 0.25 S_{market} + 0.20 S_{moat} + 0.20 S_{fin} + 0.15 S_{tech} + 0.10 S_{gtm} + 0.10 S_{risk}$$

### 2.1 Financial Modeling
- **LTV Calculation:**
  $$	ext{LTV} = rac{	ext{ACV} 	imes 	ext{Gross Margin \%}}{	ext{Annual Churn Rate}}$$
- **Payback Period (Months):**
  $$	ext{Payback} = rac{	ext{CAC}}{rac{	ext{ACV} 	imes 	ext{Gross Margin \%}}{12}}$$
- **Net Present Value (NPV):**
  $$	ext{NPV} = \sum_{t=1}^{5} rac{	ext{Net Cash Flow}_t}{(1 + r)^t} \quad (r = 12\%)$$

---

## 3. Decision Matrix

| Composite Score Range | Investment Grade / Recommendation | Strategic Guidance |
| :--- | :--- | :--- |
| **80.0 – 100.0** | `STRONG_BUY_SCALE` | High market demand, defensible moat, and mature readiness. Prioritize capital allocation and GTM scale. |
| **65.0 – 79.9** | `BUY_INVEST` | Solid fundamentals; execute targeted pilot programs and feature packaging to expand TAM. |
| **50.0 – 64.9** | `INCUBATE_VALIDATE` | Promising core technology with unproven commercial traction. Validate reference customers. |
| **40.0 – 49.9** | `MAINTAIN_HARVEST` | Cash-generative niche; limited expansion headroom. Maintain low OpEx. |
| **< 40.0** | `PIVOT_REVISE` | High customer friction, weak moat, or regulatory hurdles. Refactor architecture or divest. |
