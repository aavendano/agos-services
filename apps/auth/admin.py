from django.contrib import admin
from .models import ShopifyStoreSession

@admin.register(ShopifyStoreSession)
class ShopifyStoreSessionAdmin(admin.ModelAdmin):
    list_display = ("shop_url", "is_active", "scopes", "installed_at", "updated_at")
    list_filter = ("is_active", "installed_at")
    search_fields = ("shop_url",)
    readonly_fields = ("id", "installed_at", "updated_at")
