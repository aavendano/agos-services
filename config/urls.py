from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "service": "hi-bel",
        "mcp_gateway": "active",
        "isolation_mode": "strict_mcp_only",
    })

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("admin/", admin.site.urls),
    # Internal channel admin API
    path("api/channels/", include("apps.channels.urls")),
    # Shopify OAuth integration
    path("api/auth/shopify/", include("apps.auth.urls")),
    # OAuth toolkit endpoints
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    # MCP Gateway Endpoints (The exclusive gateway for external agents/apps)
    path("mcp/", include("apps.mcp_server.urls")),
]
