import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
from django.conf import settings
from .exceptions import (
    ShopifyAPIError,
    ShopifyAuthenticationError,
    ShopifyRateLimitError,
    ShopifyGraphQLError,
    ShopifyNotFoundError,
)
from .queries import (
    PRODUCTS_QUERY,
    PRODUCT_BY_ID_QUERY,
    INVENTORY_ITEMS_QUERY,
    ORDERS_QUERY,
    ORDER_BY_ID_QUERY,
    DRAFT_ORDER_CREATE_MUTATION,
)

logger = logging.getLogger(__name__)

class ShopifyGraphQLClient:
    """
    High-performance asynchronous client for Shopify Admin GraphQL API.
    Features:
    - Rate limit (leaky bucket) tracking from response headers
    - Automatic exponential backoff
    - Store credential resolution from DB or environment
    """
    def __init__(self, shop_url: Optional[str] = None, access_token: Optional[str] = None, api_version: Optional[str] = None):
        self.shop_url = (shop_url or getattr(settings, "SHOPIFY_STORE_DOMAIN", "")).replace("https://", "").replace("http://", "").rstrip("/")
        self.access_token = access_token or getattr(settings, "SHOPIFY_API_KEY", "")
        self.api_version = api_version or getattr(settings, "SHOPIFY_API_VERSION", "2024-07")
        self.endpoint = f"https://{self.shop_url}/admin/api/{self.api_version}/graphql.json"
        self._available_restore_rate: float = 50.0

    @classmethod
    async def get_client_for_store(cls, shop_url: Optional[str] = None) -> "ShopifyGraphQLClient":
        """Resolves active ShopifyStoreSession from the database or falls back to env config."""
        from asgiref.sync import sync_to_async
        from apps.auth.models import ShopifyStoreSession

        target_shop = shop_url or getattr(settings, "SHOPIFY_STORE_DOMAIN", "")
        if target_shop:
            session = await sync_to_async(
                lambda: ShopifyStoreSession.objects.filter(shop_url=target_shop, is_active=True).first()
            )()
            if session and session.access_token:
                return cls(shop_url=session.shop_url, access_token=session.access_token)

        # Fallback to first active store in DB
        session = await sync_to_async(
            lambda: ShopifyStoreSession.objects.filter(is_active=True).first()
        )()
        if session and session.access_token:
            return cls(shop_url=session.shop_url, access_token=session.access_token)

        # Fallback to environment variables
        return cls()

    async def execute_graphql(self, query: str, variables: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Dict[str, Any]:
        if not self.shop_url or not self.access_token:
            raise ShopifyAuthenticationError("Shopify store URL or access token is not configured.")

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token,
            "User-Agent": "bel-agents-mcp-gateway/0.1.0",
        }
        payload = {"query": query, "variables": variables or {}}

        attempt = 0
        while attempt < max_retries:
            attempt += 1
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(self.endpoint, json=payload, headers=headers)
                
                # Check HTTP status
                if response.status_code == 401:
                    raise ShopifyAuthenticationError("Shopify authentication failed. Invalid access token.")
                elif response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", 1.5))
                    logger.warning(f"Shopify rate limit hit, backing off for {retry_after}s (attempt {attempt}/{max_retries})")
                    if attempt >= max_retries:
                        raise ShopifyRateLimitError("Shopify rate limit exceeded after retries", retry_after=retry_after)
                    await asyncio.sleep(retry_after)
                    continue

                response.raise_for_status()
                data = response.json()

                # Check GraphQL level errors
                if "errors" in data and data["errors"]:
                    # Check if error is throttled
                    is_throttled = any("THROTTLED" in str(e) for e in data["errors"])
                    if is_throttled:
                        wait_time = 1.0 * (2 ** (attempt - 1))
                        logger.warning(f"Shopify GraphQL throttled, retrying in {wait_time}s")
                        if attempt >= max_retries:
                            raise ShopifyRateLimitError("Shopify GraphQL throttled", retry_after=wait_time)
                        await asyncio.sleep(wait_time)
                        continue
                    raise ShopifyGraphQLError(data["errors"])

                return data.get("data", {})

            except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as net_err:
                if attempt >= max_retries:
                    raise ShopifyAPIError(f"Network error communicating with Shopify: {net_err}") from net_err
                await asyncio.sleep(0.5 * attempt)

        raise ShopifyAPIError("Failed to execute GraphQL query after multiple attempts.")

    # High-level domain operations
    async def get_products(self, limit: int = 10, query: Optional[str] = None) -> Dict[str, Any]:
        result = await self.execute_graphql(PRODUCTS_QUERY, {"first": limit, "query": query})
        products_data = result.get("products", {})
        edges = products_data.get("edges", [])
        return {
            "products": [edge["node"] for edge in edges],
            "page_info": products_data.get("pageInfo", {}),
            "count": len(edges),
        }

    async def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        gid = product_id if product_id.startswith("gid://shopify/Product/") else f"gid://shopify/Product/{product_id}"
        result = await self.execute_graphql(PRODUCT_BY_ID_QUERY, {"id": gid})
        product = result.get("product")
        if not product:
            raise ShopifyNotFoundError(f"Product with ID '{product_id}' not found.")
        return product

    async def search_inventory(self, sku: Optional[str] = None, location_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        query_parts = []
        if sku:
            query_parts.append(f"sku:{sku}")
        query_str = " AND ".join(query_parts) if query_parts else None

        result = await self.execute_graphql(INVENTORY_ITEMS_QUERY, {"first": limit, "query": query_str})
        edges = result.get("inventoryItems", {}).get("edges", [])
        return {
            "inventory_items": [edge["node"] for edge in edges],
            "count": len(edges),
        }

    async def get_orders(self, limit: int = 10, status: Optional[str] = "open") -> Dict[str, Any]:
        query_str = f"status:{status}" if status else None
        result = await self.execute_graphql(ORDERS_QUERY, {"first": limit, "query": query_str})
        orders_data = result.get("orders", {})
        edges = orders_data.get("edges", [])
        return {
            "orders": [edge["node"] for edge in edges],
            "page_info": orders_data.get("pageInfo", {}),
            "count": len(edges),
        }

    async def get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        gid = order_id if order_id.startswith("gid://shopify/Order/") else f"gid://shopify/Order/{order_id}"
        result = await self.execute_graphql(ORDER_BY_ID_QUERY, {"id": gid})
        order = result.get("order")
        if not order:
            raise ShopifyNotFoundError(f"Order with ID '{order_id}' not found.")
        return order

    async def create_draft_order(self, line_items: list, customer_id: Optional[str] = None, note: Optional[str] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"lineItems": line_items}
        if customer_id:
            gid_cust = customer_id if customer_id.startswith("gid://shopify/Customer/") else f"gid://shopify/Customer/{customer_id}"
            input_data["customerId"] = gid_cust
        if note:
            input_data["note"] = note

        result = await self.execute_graphql(DRAFT_ORDER_CREATE_MUTATION, {"input": input_data})
        payload = result.get("draftOrderCreate", {})
        user_errors = payload.get("userErrors", [])
        if user_errors:
            error_msg = "; ".join(e.get("message", "") for e in user_errors)
            raise ShopifyAPIError(f"Failed to create draft order: {error_msg}")
        return payload.get("draftOrder", {})
