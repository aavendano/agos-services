# Deployment Profiles & Operational Runbooks

> **Compliance Standard**: STD-DOC-001  
> **Project**: [agos-services](/AADA/projects/agos-services)  
> **Runtime Spec**: [AADA-43 runtime-spec](/AADA/issues/AADA-43#document-runtime-spec)  
> **Owner**: Operations Lead · **Verification**: [AADA-46](/AADA/issues/AADA-46)

This document defines cloud deployment profiles, monthly cost estimates, and operational runbooks for the `agos-services` monorepo. It complements the quick-start guide in [DEPLOYMENT.md](./DEPLOYMENT.md).

---

## 1. Capacity Target

| Metric | Target | Notes |
|--------|--------|-------|
| Concurrent MCP agent sessions | **250** | SSE connections via `/mcp/sse` |
| CP-SAT solver throughput (AGOS tier) | 50 solves/sec | Future worker tier; not in current compose |
| Primary services in scope | `hi-bel`, `tech-commercial-analyzer` | See runtime-spec service matrix |
| Data tier | PostgreSQL 16 + Redis 7 | Required in all non-dev profiles |

**Sizing assumption**: ~2 MB RAM per idle SSE session + ~50 ms CPU bursts per tool call. At 250 sessions, plan **≥ 4 vCPU / 8 GB RAM** on a single node, or **≥ 4 app replicas** on PaaS with shared managed Postgres/Redis.

---

## 2. Deployment Profiles

### Profile A — Staging VPS (Caddy + Docker Compose)

**Best for**: Staging, internal demos, cost-predictable pre-production.

| Component | Specification |
|-----------|---------------|
| **Provider** | Hetzner CX32 / DigitalOcean 4 vCPU 8 GB / Linode Dedicated 8 GB |
| **OS** | Ubuntu 24.04 LTS |
| **Edge** | Caddy 2.x (automatic TLS, HTTP/2, SSE-friendly proxy) |
| **App runtime** | Docker Compose (`docker-compose.yml` today; unified `docker-compose.runtime.yml` per [AADA-44](/AADA/issues/AADA-44)) |
| **Process model** | Uvicorn ASGI (4 workers) behind Caddy; optional Gunicorn+Uvicorn workers for mixed WSGI/ASGI |
| **Database** | PostgreSQL 16 (container or managed add-on) |
| **Cache** | Redis 7 with AOF persistence (`appendonly yes`) |
| **Capacity** | Up to 250 MCP sessions on 4 vCPU / 8 GB |

#### Caddyfile (SSE-safe)

```caddyfile
mcp.example.com {
    encode gzip

    @sse path /mcp/sse*
    handle @sse {
        reverse_proxy web:8000 {
            flush_interval -1
            transport http {
                read_timeout 86400s
                write_timeout 86400s
            }
        }
    }

    handle {
        reverse_proxy web:8000
    }
}
```

#### Start command (VPS)

```bash
docker compose pull
docker compose up -d --build
docker compose exec web python manage.py migrate --noinput
curl -sf http://127.0.0.1:8000/health/
```

#### Environment (minimum)

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django signing; rotate quarterly |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Rate limits + session state |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `SHOPIFY_*` | Store integration credentials |
| `MCP_AUTH_REQUIRED` | `True` in all non-local profiles |

**Pros**: Lowest predictable cost, full control, SSE tuning, single-node simplicity.  
**Cons**: Manual scaling, operator owns patching and backups.

---

### Profile B — Railway (PaaS Auto-scaling)

**Best for**: Fast iteration, managed TLS, horizontal scale without VPS ops.

| Component | Specification |
|-----------|---------------|
| **Services** | `web-hibel` (Dockerfile), `analyzer` (optional second service), Railway Postgres, Railway Redis |
| **Scaling** | 0.5 vCPU / 512 MB per replica; **min 2 / max 10** replicas |
| **Start command** | `python manage.py migrate && uvicorn config.asgi:application --host 0.0.0.0 --port $PORT --workers 2` |
| **Health check** | `GET /health/` |
| **Capacity** | ~25–30 SSE sessions per replica → 8–10 replicas at 250 sessions |

#### Railway-specific env wiring

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
DEBUG=False
MCP_AUTH_REQUIRED=True
```

**Pros**: Git-push deploys, managed DB/Redis, autoscale.  
**Cons**: Per-replica cost adds up at peak; SSE long-lived connections consume replica slots.

---

### Profile C — Render (PaaS Web Service)

**Best for**: Teams already on Render; similar trade-offs to Railway.

| Component | Specification |
|-----------|---------------|
| **Web Service** | Python 3.11, Docker or native build |
| **Build** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| **Start** | `python manage.py migrate && uvicorn config.asgi:application --host 0.0.0.0 --port $PORT --workers 2` |
| **Scaling** | Manual or autoscale (Starter → Standard plans); recommend **≥ 4 instances** at 250 sessions |
| **Add-ons** | Render PostgreSQL (Starter+), external Redis (Upstash or Render Key Value) |

**Pros**: Simple UX, built-in PostgreSQL.  
**Cons**: Redis not first-class on all tiers; SSE requires Standard plan + tuned timeouts.

---

### Profile D — VPS Production (Gunicorn + Uvicorn Workers)

**Best for**: Production on owned VPS when Caddy-only Uvicorn is insufficient for mixed workloads.

```bash
gunicorn config.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --workers 4 \
  --timeout 120 \
  --graceful-timeout 30 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

Use Profile A edge (Caddy) unchanged. Increase workers only after monitoring CPU and open connections.

---

## 3. Monthly Cost Matrix (USD, estimated Aug 2026)

Estimates for **250 concurrent MCP sessions** with PostgreSQL 16 + Redis 7. Prices vary by region and commitment; treat as planning band.

| Line item | Staging VPS (single node) | PaaS Auto-scaling (Railway/Render) |
|-----------|---------------------------|-------------------------------------|
| **Compute** | $24–48 (4 vCPU / 8 GB VPS) | $80–200 (8–10 × 0.5 vCPU replicas @ ~$10–20/mo each) |
| **PostgreSQL** | $0 (container on same VPS) or $15 (managed micro) | $15–50 (managed, backups included) |
| **Redis** | $0 (container) or $10 (managed 256 MB) | $10–25 (managed / Upstash) |
| **Egress / TLS** | ~$0 (included) | ~$5–15 |
| **Backups & monitoring** | $0–5 (self-managed pg_dump + Uptime Kuma) | $0–10 (provider add-ons) |
| **Total (typical)** | **$24–48/mo** | **$110–290/mo** |
| **Total (managed data tier on VPS)** | **$49–73/mo** | — |

### Recommendation by phase

| Phase | Profile | Est. monthly |
|-------|---------|--------------|
| Local / CI | SQLite + LocMem (dev defaults) | $0 |
| Staging & pilot | **Profile A** VPS | $24–48 |
| Production (low traffic) | Profile A + managed DB backups | $49–73 |
| Production (elastic peak) | **Profile B or C** with autoscale | $110–290 |

**Budget guardrail**: Alert at **$150/mo** PaaS spend; cap replicas at 10 unless board approval ([Chief of Staff](/AADA/agents/chief-of-staff)).

---

## 4. Operational Runbooks

### 4.1 Database Migration Runbook

**Scope**: PostgreSQL schema changes via Django migrations (`hi-bel`).

**Preconditions**

- [ ] Migration reviewed in PR; backup taken within last 24 h
- [ ] `python manage.py migrate --plan` output captured in deploy log
- [ ] Maintenance window communicated if table locks expected > 30 s

**Procedure (VPS / Docker)**

```bash
# 1. Backup
docker compose exec postgres pg_dump -U postgres -Fc hi_bel > "backup_$(date +%Y%m%d_%H%M).dump"

# 2. Dry-run plan
docker compose exec web python manage.py migrate --plan

# 3. Apply
docker compose exec web python manage.py migrate --noinput

# 4. Verify
docker compose exec web python manage.py showmigrations | tail -5
curl -sf https://mcp.example.com/health/
```

**Procedure (Railway / Render)**

1. Trigger deploy with start command including `migrate` (see profiles above), **or** run one-off shell: `python manage.py migrate --noinput`.
2. Watch deploy logs for migration errors.
3. Hit `/health/`; confirm admin login and one MCP tool smoke test.

**Rollback**

1. Stop traffic (Caddy maintenance page or scale web to 0).
2. Restore dump: `pg_restore -d hi_bel --clean backup_YYYYMMDD.dump`
3. Redeploy previous container image / git SHA.
4. Document incident in issue thread; link to [AADA-46](/AADA/issues/AADA-46) if governance review required.

---

### 4.2 Secret Rotation Runbook

**Secrets in scope**: `SECRET_KEY`, `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET`, Postgres password, Redis password, MCP client tokens (via Django admin).

| Secret | Rotation cadence | Procedure |
|--------|------------------|-----------|
| `SECRET_KEY` | Quarterly | Generate new 64-char key → update env → rolling restart all web replicas → invalidate sessions |
| `SHOPIFY_API_*` | On compromise or Shopify rotation | Update in Shopify Partner Dashboard → update env → restart web → verify OAuth callback |
| `DATABASE_URL` password | Quarterly or on personnel change | `ALTER USER … PASSWORD` in Postgres → update env → rolling restart |
| `REDIS_URL` password | Quarterly | Update Redis ACL → update env → restart web (cache miss acceptable) |
| MCP client tokens | On leak or offboarding | Django Admin → MCPClient → regenerate token → notify client owner |

**Zero-trust rules**

- Never commit secrets; validate with `detect-secrets` / CI scan ([AADA-46](/AADA/issues/AADA-46)).
- Propose production values via Paperclip secret proposals, not issue comments.
- After rotation: run smoke test — MCP SSE connect + one permitted tool call.

**Rolling restart (VPS)**

```bash
docker compose up -d --no-deps --build web
docker compose logs -f web
```

**Rolling restart (PaaS)**: Redeploy service after env var update; stagger if multi-service.

---

### 4.3 Redis Contingency Runbook

**Symptoms**: Elevated 5xx on MCP routes, rate-limit failures, health check shows cache errors, `ConnectionError` to Redis in logs.

**Impact**: Rate limiting falls back to LocMem **only if `REDIS_URL` unset**; in production with `REDIS_URL` set, cache failures propagate — treat as **SEV-2**.

#### Scenario A — Redis unreachable (network / container down)

1. **Confirm**: `docker compose ps redis` or provider dashboard.
2. **Restart Redis**:
   ```bash
   docker compose restart redis
   # or PaaS: restart Redis add-on
   ```
3. **Verify**: `redis-cli -u "$REDIS_URL" PING` → `PONG`.
4. **Restart web** to clear stale connection pools:
   ```bash
   docker compose restart web
   ```
5. Monitor MCP session count and error rate for 15 min.

#### Scenario B — Redis data corruption / bad deploy

1. Stop web replicas (prevent writes).
2. If AOF enabled: `redis-check-aof --fix appendonly.aof` or restore from last RDB snapshot.
3. If no backup: flush cache ( **rate limits reset** — expect brief Shopify API pressure ):
   ```bash
   redis-cli -u "$REDIS_URL" FLUSHDB
   ```
4. Restart web; notify Governance if flush occurred in production.

#### Scenario C — Redis permanently lost ( disaster )

1. Provision new Redis instance; update `REDIS_URL` in env.
2. Rolling restart all app replicas.
3. Accept cold-cache period (15–30 min): tighter effective rate limits until buckets refill.
4. No PostgreSQL data loss; MCP auth remains in Postgres.

#### Scenario D — Degraded mode (emergency only, board-approved)

If Redis provider outage exceeds SLA and board approves temporary degradation:

1. Remove `REDIS_URL` from env **only with explicit approval** — app falls back to LocMem per `config/settings.py` (per-replica limits, not global).
2. Scale down concurrent MCP clients or reduce `rate_limit_rpm` in Django admin.
3. Restore `REDIS_URL` within 24 h; post-incident review to [AADA-46](/AADA/issues/AADA-46).

**Prevention**

- Enable AOF: `redis-server --appendonly yes --appendfsync everysec`
- Daily RDB snapshot to object storage (VPS cron or provider backup)
- Alert on Redis memory > 80% and connection count > 200

---

## 5. Health & Smoke Checks (all profiles)

| Endpoint | Service | Expected |
|----------|---------|----------|
| `GET /health/` | hi-bel | 200, `status: healthy` |
| `GET /api/health` | tech-commercial-analyzer | 200 (when deployed) |
| `GET /mcp/sse` | hi-bel | 401/403 without token; SSE stream with valid MCP client |

Post-deploy checklist:

```bash
curl -sf "$BASE_URL/health/"
pytest tests/ --quiet   # hi-bel unit suite from repo root
```

---

## 6. Related Documents

| Document | Purpose |
|----------|---------|
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Quick deploy steps (Railway, Render, Nginx) |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Zero-trust MCP isolation policy |
| [MCP_GUIDE.md](./MCP_GUIDE.md) | Client configuration |
| [AADA-43 runtime-spec](/AADA/issues/AADA-43#document-runtime-spec) | Authoritative sizing & service matrix |
| [AADA-44](/AADA/issues/AADA-44) | Containerized runtime stack implementation |
| [AADA-46](/AADA/issues/AADA-46) | Governance verification & audit |

---

## 7. Acceptance Checklist (AADA-45)

- [x] Deployment profiles documented (VPS/Caddy, Railway, Render, Gunicorn+Uvicorn)
- [x] Monthly cost matrix (Staging VPS vs PaaS auto-scaling)
- [x] Runbooks: database migrations, secret rotation, Redis contingency
