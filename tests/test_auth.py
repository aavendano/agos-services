import pytest
from apps.auth.models import ShopifyStoreSession
from apps.auth.services import ShopifyAuthService

@pytest.mark.django_db
class TestShopifyAuth:
    def test_store_session_creation(self, active_store_session):
        assert active_store_session.shop_url == "test-store.myshopify.com"
        assert active_store_session.is_active is True

    def test_build_install_url(self, settings):
        settings.SHOPIFY_API_KEY = "test_api_key"
        settings.SHOPIFY_SCOPES = "read_products"
        settings.SHOPIFY_REDIRECT_URI = "https://example.com/callback"

        url = ShopifyAuthService.build_install_url("demo.myshopify.com", "state123")
        assert "https://demo.myshopify.com/admin/oauth/authorize?" in url
        assert "client_id=test_api_key" in url
        assert "state=state123" in url

    def test_verify_hmac_validation(self, settings):
        settings.SHOPIFY_API_SECRET = "secret_key"
        import hmac
        import hashlib

        query = {"shop": "demo.myshopify.com", "timestamp": "123456"}
        sorted_str = "shop=demo.myshopify.com&timestamp=123456"
        computed = hmac.new(b"secret_key", sorted_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        valid_params = dict(query, hmac=computed)
        assert ShopifyAuthService.verify_hmac(valid_params) is True

        invalid_params = dict(query, hmac="wrong_signature")
        assert ShopifyAuthService.verify_hmac(invalid_params) is False
