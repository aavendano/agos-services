# Client Configuration Guide: Model Context Protocol (MCP)

This guide describes how to connect external AI tools and IDEs to the `hi-bel` Shopify MCP Gateway.

## 1. Authentication & Tokens

All external requests require an active `MCPClient` token. Obtain your client token from the Django Admin (`/admin/channels/mcpclient/`) or via the administrative provisioning API.

---

## 2. Connecting Claude Desktop

Add the following entry to your Claude Desktop configuration file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "shopify-mcp": {
      "command": "python",
      "args": [
        "/path/to/agos-services/manage.py",
        "run_mcp_server",
        "--transport",
        "stdio"
      ],
      "env": {
        "DATABASE_URL": "postgres://postgres:postgres@localhost:5432/hi_bel",
        "SHOPIFY_API_KEY": "shpat_your_token_here",
        "SHOPIFY_STORE_DOMAIN": "your-store.myshopify.com"
      }
    }
  }
}
```

---

## 3. Connecting Cursor IDE

In Cursor:
1. Open **Settings > Cursor Settings > Features > MCP**.
2. Click **+ Add New MCP Server**.
3. Choose type **SSE**:
   - **Name:** `hi-bel-shopify`
   - **URL:** `http://localhost:8000/mcp/sse?token=<YOUR_MCP_CLIENT_UUID_TOKEN>` (or your production URL with HTTPS).
4. Save and verify the tools appear in the MCP list.

---

## 4. Available MCP Tools Reference

| Tool Name | Parameters | Description |
|---|---|---|
| `get_products` | `limit: int`, `query: str` | Query Shopify products with title/tag filters and pagination. |
| `get_product_by_id` | `product_id: str` | Fetch complete product details and variants by ID. |
| `search_inventory` | `sku: str`, `location_id: str`, `limit: int` | Check available inventory levels across warehouses. |
| `get_orders` | `limit: int`, `status: str` | Retrieve customer orders filtered by status (`open`, `closed`, `any`). |
| `get_order_by_id` | `order_id: str` | Retrieve order line items, shipping address, and payment status. |
| `create_draft_order` | `line_items: list`, `customer_id: str`, `note: str` | Create a draft order for agentic checkout workflows. |
