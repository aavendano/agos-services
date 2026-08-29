import json
import logging
from typing import Optional, Dict, Any, List
from mcp.server.mcpserver import MCPServer
from apps.mcp_server.middleware import PrivilegeGate, PermissionDeniedError, AuthenticationRequiredError
from apps.mcp_server.tools import (
    handle_get_products,
    handle_get_product_by_id,
    handle_search_inventory,
    handle_get_orders,
    handle_get_order_by_id,
    handle_create_draft_order,
)

logger = logging.getLogger(__name__)

def create_mcp_server() -> MCPServer:
    """
    Instantiates and configures the bel-agents Shopify MCP Server.
    Registers all e-commerce tools with schemas and privilege enforcement.
    """
    server = MCPServer(
        name="bel-agents-shopify-mcp",
        version="0.1.0",
        instructions=(
            "bel-agents is a secure e-commerce gateway for Shopify. "
            "All operations require active client authentication and granted tool privileges."
        ),
    )

    @server.tool(
        name="get_products",
        description="Query Shopify products catalog with optional search filter and pagination limit.",
    )
    async def get_products(limit: int = 10, query: Optional[str] = None, client_token: Optional[str] = None) -> str:
        client = await PrivilegeGate.authenticate_token(client_token)
        result = await handle_get_products(client=client, limit=limit, query=query)
        return json.dumps(result, indent=2)

    @server.tool(
        name="get_product_by_id",
        description="Retrieve detailed product information, including variants and prices, by Shopify product ID.",
    )
    async def get_product_by_id(product_id: str, client_token: Optional[str] = None) -> str:
        client = await PrivilegeGate.authenticate_token(client_token)
        result = await handle_get_product_by_id(client=client, product_id=product_id)
        return json.dumps(result, indent=2)

    @server.tool(
        name="search_inventory",
        description="Search inventory levels across locations by SKU or inventory item ID.",
    )
    async def search_inventory(sku: Optional[str] = None, location_id: Optional[str] = None, limit: int = 20, client_token: Optional[str] = None) -> str:
        client = await PrivilegeGate.authenticate_token(client_token)
        result = await handle_search_inventory(client=client, sku=sku, location_id=location_id, limit=limit)
        return json.dumps(result, indent=2)

    @server.tool(
        name="get_orders",
        description="List customer orders filtered by status (open, closed, any) and pagination limit.",
    )
    async def get_orders(limit: int = 10, status: Optional[str] = "open", client_token: Optional[str] = None) -> str:
        client = await PrivilegeGate.authenticate_token(client_token)
        result = await handle_get_orders(client=client, limit=limit, status=status)
        return json.dumps(result, indent=2)

    @server.tool(
        name="get_order_by_id",
        description="Retrieve complete order details by Shopify order ID.",
    )
    async def get_order_by_id(order_id: str, client_token: Optional[str] = None) -> str:
        client = await PrivilegeGate.authenticate_token(client_token)
        result = await handle_get_order_by_id(client=client, order_id=order_id)
        return json.dumps(result, indent=2)

    @server.tool(
        name="create_draft_order",
        description="Create a draft order in Shopify with specified line items, optional customer ID, and notes.",
    )
    async def create_draft_order(
        line_items: List[Dict[str, Any]],
        customer_id: Optional[str] = None,
        note: Optional[str] = None,
        client_token: Optional[str] = None,
    ) -> str:
        client = await PrivilegeGate.authenticate_token(client_token)
        result = await handle_create_draft_order(
            client=client,
            line_items=line_items,
            customer_id=customer_id,
            note=note,
        )
        return json.dumps(result, indent=2)

    return server

mcp_server_instance = create_mcp_server()
