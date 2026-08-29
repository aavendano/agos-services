from django.urls import path
from .views import ShopifyInstallView, ShopifyCallbackView, ShopifyStatusView

urlpatterns = [
    path("install/", ShopifyInstallView.as_view(), name="shopify_install"),
    path("callback/", ShopifyCallbackView.as_view(), name="shopify_callback"),
    path("status/", ShopifyStatusView.as_view(), name="shopify_status"),
]
