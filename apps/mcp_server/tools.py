import json
import logging
from typing import Optional, List, Dict, Any
from apps.shopify_api.client import ShopifyGraphQLClient
from apps.mcp_server.middleware import PrivilegeGate, MCPClient

logger = logging.getLogger(__name__)

# Tool implementation functions with privilege enforcement
async def handle_get_products(client: MCPClient, limit: int = 10, query: Optional[str] = None) -> Dict[str, Any]:
    await PrivilegeGate.verify_tool_permission(client, "get_products")
    shopify_client = await ShopifyGraphQLClient.get_client_for_store()
    return await shopify_client.get_products(limit=limit, query=query)


async def handle_get_product_by_id(client: MCPClient, product_id: str) -> Dict[str, Any]:
    await PrivilegeGate.verify_tool_permission(client, "get_product_by_id")
    shopify_client = await ShopifyGraphQLClient.get_client_for_store()
    return await shopify_client.get_product_by_id(product_id=product_id)


async def handle_search_inventory(client: MCPClient, sku: Optional[str] = None, location_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    await PrivilegeGate.verify_tool_permission(client, "search_inventory")
    shopify_client = await ShopifyGraphQLClient.get_client_for_store()
    return await shopify_client.search_inventory(sku=sku, location_id=location_id, limit=limit)


async def handle_get_orders(client: MCPClient, limit: int = 10, status: Optional[str] = "open") -> Dict[str, Any]:
    await PrivilegeGate.verify_tool_permission(client, "get_orders")
    shopify_client = await ShopifyGraphQLClient.get_client_for_store()
    return await shopify_client.get_orders(limit=limit, status=status)


async def handle_get_order_by_id(client: MCPClient, order_id: str) -> Dict[str, Any]:
    await PrivilegeGate.verify_tool_permission(client, "get_order_by_id")
    shopify_client = await ShopifyGraphQLClient.get_client_for_store()
    return await shopify_client.get_order_by_id(order_id=order_id)


async def handle_create_draft_order(
    client: MCPClient,
    line_items: List[Dict[str, Any]],
    customer_id: Optional[str] = None,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    await PrivilegeGate.verify_tool_permission(client, "create_draft_order")
    shopify_client = await ShopifyGraphQLClient.get_client_for_store()
    return await shopify_client.create_draft_order(
        line_items=line_items,
        customer_id=customer_id,
        note=note,
    )
