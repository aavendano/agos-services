import pytest
import respx
import httpx
from apps.shopify_api.client import ShopifyGraphQLClient
from apps.shopify_api.exceptions import ShopifyAuthenticationError, ShopifyRateLimitError, ShopifyNotFoundError

@pytest.mark.asyncio
class TestShopifyGraphQLClient:
    async def test_missing_credentials_raises_auth_error(self):
        client = ShopifyGraphQLClient(shop_url="", access_token="")
        with pytest.raises(ShopifyAuthenticationError):
            await client.get_products()

    @respx.mock
    async def test_get_products_success(self):
        client = ShopifyGraphQLClient(shop_url="test.myshopify.com", access_token="token123")
        respx.post("https://test.myshopify.com/admin/api/2024-07/graphql.json").respond(
            status_code=200,
            json={
                "data": {
                    "products": {
                        "edges": [
                            {
                                "node": {
                                    "id": "gid://shopify/Product/1",
                                    "title": "Snowboard",
                                    "handle": "snowboard",
                                    "status": "ACTIVE",
                                    "totalInventory": 42,
                                    "variants": {"edges": []}
                                }
                            }
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": "xyz"}
                    }
                }
            }
        )

        res = await client.get_products(limit=5)
        assert res["count"] == 1
        assert res["products"][0]["title"] == "Snowboard"

    @respx.mock
    async def test_get_product_by_id_not_found(self):
        client = ShopifyGraphQLClient(shop_url="test.myshopify.com", access_token="token123")
        respx.post("https://test.myshopify.com/admin/api/2024-07/graphql.json").respond(
            status_code=200,
            json={"data": {"product": None}}
        )

        with pytest.raises(ShopifyNotFoundError):
            await client.get_product_by_id("999999")

    @respx.mock
    async def test_rate_limit_retry_and_raise(self):
        client = ShopifyGraphQLClient(shop_url="test.myshopify.com", access_token="token123")
        respx.post("https://test.myshopify.com/admin/api/2024-07/graphql.json").respond(
            status_code=429,
            headers={"Retry-After": "0.01"}
        )

        with pytest.raises(ShopifyRateLimitError):
            await client.execute_graphql("query { shop { name } }", max_retries=2)
