import hmac
import hashlib
import urllib.parse
from django.conf import settings
import httpx

class ShopifyAuthService:
    @staticmethod
    def verify_hmac(query_params: dict) -> bool:
        if not settings.SHOPIFY_API_SECRET:
            return True
        params = query_params.copy()
        signature = params.pop("hmac", None)
        if isinstance(signature, list):
            signature = signature[0]
        if not signature:
            return False
        
        # Sort and concatenate
        sorted_params = "&".join(f"{k}={','.join(v) if isinstance(v, list) else v}" for k, v in sorted(params.items()))
        calculated_hmac = hmac.new(
            settings.SHOPIFY_API_SECRET.encode("utf-8"),
            sorted_params.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(calculated_hmac, signature)

    @staticmethod
    def build_install_url(shop: str, state: str) -> str:
        shop = shop.replace("https://", "").replace("http://", "").rstrip("/")
        params = {
            "client_id": settings.SHOPIFY_API_KEY,
            "scope": settings.SHOPIFY_SCOPES,
            "redirect_uri": settings.SHOPIFY_REDIRECT_URI,
            "state": state,
        }
        query_string = urllib.parse.urlencode(params)
        return f"https://{shop}/admin/oauth/authorize?{query_string}"

    @staticmethod
    async def exchange_code_for_token(shop: str, code: str) -> dict:
        shop = shop.replace("https://", "").replace("http://", "").rstrip("/")
        url = f"https://{shop}/admin/oauth/access_token"
        payload = {
            "client_id": settings.SHOPIFY_API_KEY,
            "client_secret": settings.SHOPIFY_API_SECRET,
            "code": code,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
