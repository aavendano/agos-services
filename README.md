# hi-bel: Governed Shopify MCP Integration Gateway

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.1](https://img.shields.io/badge/django-5.1-green.svg)](https://www.djangoproject.com/)
[![MCP 2.x](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`agos-services` is a **monorepo** of governed internal services for AA Digital Business. The primary production service is **`hi-bel`**, a Model Context Protocol (MCP) integration gateway for Shopify e-commerce. Additional services live under `services/` and share the root Python virtual environment.

---

## Monorepo Layout

| Path | Service | Description |
|------|---------|-------------|
| `config/`, `apps/`, `tests/` | **hi-bel** | Governed Shopify MCP gateway (Django + Starlette SSE) |
| `services/tech-commercial-analyzer/` | **tech-eval** | Commercial potential scoring, DCF engine, and executive dashboard |

Each service owns its tests and documentation. Root `pytest` runs **hi-bel only**; run service tests from that service directory (see [Testing](#testing)).

---

## hi-bel Overview

`hi-bel` provides external AI agents (Claude Desktop, Cursor, autonomous agents) secure, governed, and rate-limited access to Shopify stores over Server-Sent Events (SSE) and stdio transports.

---

## Key Features

- **Strict MCP Channel Isolation:** External applications connect **strictly and exclusively** via the Model Context Protocol. No external bypass REST endpoints exist.
- **Granular Privilege Engine:** Granular permission matrix (`ToolPermission`) per client token (`MCPClient`), allowing fine-grained authorization (e.g. read-only catalog access vs. draft order creation).
- **Asynchronous Shopify GraphQL Client:** High-performance `httpx` async client with automatic leaky-bucket rate limiting, retry backoff, and pagination.
- **Shopify Custom App OAuth:** Complete OAuth 2.0 handshake with HMAC signature verification and persistent multi-store session handling.
- **Multi-Target Deployment:** Ready for Railway, Render, Docker, and VPS (Gunicorn/Uvicorn ASGI + Nginx).

---

## Project Structure

```
agos-services/
├── config/
│   ├── settings.py            # Django configuration with PostgreSQL/Redis support
│   ├── urls.py                # Internal admin routes & MCP mounting
│   ├── asgi.py                # ASGI application combining Django & Starlette SSE
│   └── wsgi.py
├── apps/
│   ├── channels/              # MCP Client provisioning & ToolPermission ORM
│   ├── mcp_server/            # Model Context Protocol Engine & Handlers
│   ├── shopify_api/           # Shopify GraphQL Admin API Adapter
│   └── auth/                  # Shopify OAuth & Django OAuth Toolkit integration
├── services/
│   └── tech-commercial-analyzer/   # Commercial valuation engine (CLI + FastAPI)
│       ├── analyzer/          # Scoring engine, financials, Monte Carlo, API
│       ├── bin/tech-eval        # CLI entrypoint
│       ├── data/technologies/   # Pre-loaded technology manifests
│       ├── tests/               # Service test suite (12 tests)
│       └── README.md
├── docs/
│   ├── ARCHITECTURE.md        # Technical architecture blueprint (STD-DOC-001)
│   ├── MCP_GUIDE.md           # Client setup guide for Cursor, Claude, Antigravity
│   └── DEPLOYMENT.md          # Deployment guide for Railway, Render, VPS
├── tests/                     # hi-bel test suite (19 tests)
│   ├── conftest.py            # Pytest fixtures and mock DB setup
│   ├── test_auth.py
│   ├── test_channels.py
│   ├── test_mcp_server.py
│   └── test_shopify_api.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── pyproject.toml             # Root pytest config (hi-bel testpaths)
└── requirements.txt
```

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL & Redis (optional for dev; SQLite/LocMem fallback is built-in)

### 2. Installation
```bash
git clone https://github.com/aavendano/agos-services.git
cd agos-services

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Shopify credentials
```

### 4. Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser & Provision MCP Client
```bash
python manage.py createsuperuser
python manage.py runserver
```
Visit `http://localhost:8000/admin/` to create an `MCPClient` and grant `ToolPermission` records.

### 6. Run Test Suite

**hi-bel** (from repo root — default `testpaths` in `pyproject.toml`):

```bash
pytest tests/    # or simply: pytest
```

**tech-commercial-analyzer** (from service directory):

```bash
cd services/tech-commercial-analyzer
pytest
```

**Run both suites:**

```bash
pytest tests/ && (cd services/tech-commercial-analyzer && pytest)
```

See [services/tech-commercial-analyzer/README.md](services/tech-commercial-analyzer/README.md) for CLI and dashboard usage.

---

## Documentation

- [Architecture & Isolation Policy](docs/ARCHITECTURE.md)
- [Client Setup Guide (Cursor / Claude)](docs/MCP_GUIDE.md)
- [Deployment Guide (Railway / Render / VPS)](docs/DEPLOYMENT.md)

---

## License

MIT
