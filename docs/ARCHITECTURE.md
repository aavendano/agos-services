# Architecture Blueprint: `hi-bel` Shopify MCP Gateway

## 1. Overview & System Isolation Policy

`hi-bel` is an enterprise-grade AI integration gateway built on **Django 5**, **Django REST Framework**, and the **Python MCP SDK (`mcp`)**. It exposes governed Shopify e-commerce capabilities to external AI agents and IDEs (such as Claude Desktop, Cursor, and autonomous agent platforms).

### Strict Gateway Isolation Principle
- **No Direct REST Bypass:** External consumer applications and AI agents are strictly isolated from internal backend APIs. External clients **must** communicate exclusively via the **Model Context Protocol (MCP)** over Server-Sent Events (`/mcp/sse` and `/mcp/messages/`).
- **Administrative Separation:** Internal management (such as client token provisioning, permission toggles, and store OAuth sessions) is restricted to the protected Django Admin / DRF endpoints accessed only by authenticated administrators.
- **Zero-Trust Privilege Gate:** Every tool invocation received over the MCP transport is intercepted and checked against active database records in `ToolPermission` before executing GraphQL operations against Shopify.

```
┌─────────────────────────────────────────────────────────────┐
│                      External Clients                       │
│       (Claude Desktop, Cursor IDE, Autonomous Agents)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                       [Only Channel: MCP]
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               hi-bel ASGI Gateway (Uvicorn)                 │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │     Starlette SSE Transport & MCP Protocol Engine     │  │
│  │   /mcp/sse (GET)  │  /mcp/messages/ (POST)            │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │       Strict PrivilegeGate & Security Middleware      │  │
│  │   - Validates MCPClient UUID token                    │  │
│  │   - Enforces ToolPermission.allowed == True           │  │
│  │   - Checks client rate limits                         │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  MCP Tool Suite                       │  │
│  │  - get_products        - search_inventory             │  │
│  │  - get_product_by_id   - create_draft_order           │  │
│  │  - get_orders          - get_order_by_id              │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │     Async Shopify GraphQL Admin Client (httpx)        │  │
│  │   - Leaky-bucket cost & rate-limit backoff            │  │
│  │   - Automatic retry & cursor pagination               │  │
│  └───────────────────────────┬───────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │   Shopify Admin GraphQL API  │
                └──────────────────────────────┘
```

---

## 2. Core Modules & Data Models

### 2.1 `apps.channels` (Governance & Client Management)
- **`MCPClient`**:
  - `id`: UUID primary key.
  - `name`: Human-readable identifier (e.g. `Cursor IDE Lead`, `Claude Desktop`).
  - `token`: Unique UUID secret token provided in client headers.
  - `is_active`: Boolean flag allowing instant revocation.
  - `rate_limit_rpm`: Request-per-minute throttle ceiling.
- **`ToolPermission`**:
  - `client`: Foreign key to `MCPClient`.
  - `tool_name`: Identifier matching the registered MCP tool.
  - `allowed`: Explicit Boolean grant.

### 2.2 `apps.mcp_server` (MCP Server & Privilege Gate)
- **`PrivilegeGate`**: Middleware enforcing authentication and permission authorization on every tool call.
- **`transport.py`**: Starlette SSE transport handler routing requests to `MCPServer`.
- **`tools.py`**: High-level tool implementations wrapping the Shopify GraphQL client.

### 2.3 `apps.shopify_api` (Shopify GraphQL Client)
- **`ShopifyGraphQLClient`**: Async `httpx` client handling Shopify Admin API queries and mutations. Includes automatic rate-limit detection and exponential backoff retry.

### 2.4 `apps.auth` (Shopify Custom App OAuth)
- **`ShopifyStoreSession`**: Persistent record storing encrypted offline access tokens and approved OAuth scopes.
- **`ShopifyAuthService`**: Handles HMAC query parameter verification and OAuth authorization code exchange.

---

## 3. Security Standards

1. **Token Security:** Tokens are generated as cryptographically strong UUID4 strings and stored indexed in PostgreSQL.
2. **Denial by Default:** Any tool not explicitly granted in `ToolPermission` returns an immediate `PermissionDeniedError` to the caller.
3. **Transport Encryption:** All production traffic must terminate TLS (HTTPS/WSS) via Nginx or Cloudflare.
