from django.apps import AppConfig

class ShopifyApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shopify_api"
    verbose_name = "Shopify GraphQL API Client"
