# Multi-Service Containerized Runtime Specification

> **Compliance Standard**: STD-DOC-001  
> **Project**: [agos-services](/AADA/projects/agos-services)  
> **Runtime Spec**: [AADA-43 runtime-spec](/AADA/issues/AADA-43#document-runtime-spec)  
> **Owner**: Agent Platform Engineer (`adeea6f6-0178-4745-9963-fb13ad2778c8`)  
> **Verification**: Governance & Verification Lead ([AADA-46](/AADA/issues/AADA-46))

---

## 1. Overview & Architecture

The `agos-services` monorepo provides a unified multi-service containerized runtime stack orchestrated via `docker-compose.runtime.yml`. The architecture integrates core ecosystem services, relational persistence, in-memory caching, and strict zero-trust MCP gateway isolation.

```
                         ┌─────────────────────────────────────────┐
                         │             Inbound Clients             │
                         │    (Claude Desktop, Cursor, Agents)     │
                         └────────────────────┬────────────────────┘
                                              │ Authenticated MCP / HTTP
                                              ▼
                         ┌─────────────────────────────────────────┐
                         │       Docker Bridge (agos-runtime)      │
                         └────────────┬───────────────┬────────────┘
                                      │               │
                     ┌────────────────┴─────┐   ┌─────┴────────────────┐
                     │      web-hibel       │   │       analyzer       │
                     │  (Django 5 ASGI MCP) │   │    (FastAPI Engine)  │
                     │      Port: 8000      │   │      Port: 8001      │
                     └────────┬─────────────┘   └──────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
         ┌───────────────────┐ ┌───────────────────┐
         │        db         │ │       redis       │
         │  (PostgreSQL 16)  │ │     (Redis 7)     │
         │    Port: 5432     │ │    Port: 6379     │
         └───────────────────┘ └───────────────────┘
```

---

## 2. Services Matrix

| Service | Container Name | Base Image / Context | Port Binding | Health Check Endpoint / Probe | Purpose |
|---|---|---|---|---|---|
| `web-hibel` | `web-hibel` | Root `Dockerfile` (Python 3.11-slim) | `${WEB_HIBEL_PORT:-8000}:8000` | `GET http://localhost:8000/health/` | Django 5 MCP Gateway with Shopify integration and OAuth2 provider |
| `analyzer` | `analyzer` | `services/tech-commercial-analyzer/Dockerfile` | `${ANALYZER_PORT:-8001}:8000` | `GET http://localhost:8000/api/health` | FastAPI Commercial Potential & Valuation Engine with web dashboard |
| `db` | `db` | `postgres:16-alpine` | `${POSTGRES_PORT:-5432}:5432` | `pg_isready -U postgres -d agos_db` | Relational state persistence for MCP permissions, clients, and OAuth |
| `redis` | `redis` | `redis:7-alpine` | `${REDIS_PORT:-6379}:6379` | `redis-cli ping` | In-memory token bucket rate limiting, SSE session tracking, and cache |

---

## 3. Zero-Trust Isolation & Security Policies

1. **Strict MCP Gateway Access**: External AI agents and clients interact exclusively through the authenticated MCP endpoints (`/mcp/sse` and `/mcp/messages`). Direct database or internal REST access by unauthenticated actors is strictly prevented.
2. **Health Endpoints**:
   - `web-hibel`: `http://localhost:8000/healthz`, `/health/`, and `/api/health/` returns JSON with service name, health status, strict MCP isolation mode, and active DB/Redis probes.
   - `analyzer`: `http://localhost:8000/healthz` and `/api/health` returns operational status and version.
3. **Database & Cache Isolation**: The `db` and `redis` services are attached to the `agos-runtime` bridge network, allowing secure inter-container communication while isolating internal services from external exposure when deployed in production.

---

## 4. Configuration & Environment Variables

All services consume environment variables defined in `.env.example`:

| Variable | Default Value | Description |
|---|---|---|
| `DEBUG` | `False` (prod) / `True` (dev) | Django debug mode |
| `SECRET_KEY` | *(Required)* | Django cryptographic signing key |
| `ALLOWED_HOSTS` | `*` / `localhost,127.0.0.1` | Allowed HTTP host headers |
| `DATABASE_URL` | `postgres://postgres:postgres@db:5432/agos_db` | PostgreSQL connection URI |
| `POSTGRES_DB` | `agos_db` | PostgreSQL default database name |
| `POSTGRES_USER` | `postgres` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_PORT` | `5432` | Host port mapping for PostgreSQL |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URI |
| `REDIS_PORT` | `6379` | Host port mapping for Redis |
| `WEB_HIBEL_PORT` | `8000` | Host port mapping for `web-hibel` service |
| `ANALYZER_PORT` | `8001` | Host port mapping for `analyzer` service |
| `ANALYZER_HOST` | `0.0.0.0` | Bind host for analyzer FastAPI server |
| `SHOPIFY_API_KEY` | *(Configurable)* | Shopify app API key |
| `SHOPIFY_API_SECRET` | *(Configurable)* | Shopify app API secret |
| `SHOPIFY_STORE_DOMAIN` | *(Configurable)* | Target myshopify.com domain |
| `MCP_SERVER_NAME` | `hi-bel-shopify-mcp` | MCP server registration name |
| `MCP_SERVER_VERSION` | `0.1.0` | MCP server semantic version |
| `MCP_AUTH_REQUIRED` | `True` | Enforce OAuth/bearer auth on MCP routes |

---

## 5. Runtime Lifecycle Commands

### Starting the Full Stack
```bash
# Build and start all services in detached mode
docker compose -f docker-compose.runtime.yml up -d --build
```

### Verifying Service Health
```bash
# Inspect container status and healthchecks
docker compose -f docker-compose.runtime.yml ps

# Check individual service logs
docker compose -f docker-compose.runtime.yml logs -f web-hibel
docker compose -f docker-compose.runtime.yml logs -f analyzer
```

### Running Migrations & Management Commands
```bash
# Execute Django migrations inside the running web-hibel container
docker compose -f docker-compose.runtime.yml exec web-hibel python manage.py migrate
```

### Stopping the Stack
```bash
# Stop containers without removing persistent volumes
docker compose -f docker-compose.runtime.yml down

# Stop and remove persistent data volumes (caution: wipes db and redis data)
docker compose -f docker-compose.runtime.yml down -v
```

---

## 6. Verification & Test Execution

Both independent test suites pass cleanly across the monorepo:

1. **`hi-bel` Gateway Test Suite**:
   ```bash
   uv run pytest tests/
   # Result: 20 passed
   ```

2. **`tech-commercial-analyzer` Test Suite**:
   ```bash
   uv run --directory services/tech-commercial-analyzer pytest
   # Result: 13 passed
   ```

3. **Total Monorepo Test Baseline**: **33 passed**.

