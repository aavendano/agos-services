import uuid
from django.db import models

class ShopifyStoreSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop_url = models.CharField(max_length=255, unique=True, db_index=True)
    access_token = models.CharField(max_length=255)
    scopes = models.TextField(default="")
    is_active = models.BooleanField(default=True)
    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shopify_store_sessions"
        ordering = ["-updated_at"]
        verbose_name = "Shopify Store Session"
        verbose_name_plural = "Shopify Store Sessions"

    def __str__(self):
        return f"{self.shop_url} ({'Active' if self.is_active else 'Inactive'})"
