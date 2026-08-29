import logging
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import redis

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check endpoint verifying application readiness,
    database connectivity, and Redis cache connectivity.
    """
    db_status = "ok"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        logger.warning(f"Healthcheck DB probe error: {e}")
        db_status = f"error: {str(e)}"

    redis_status = "ok"
    redis_url = getattr(settings, "REDIS_URL", None)
    if redis_url:
        try:
            r = redis.Redis.from_url(redis_url, socket_timeout=2)
            r.ping()
        except Exception as e:
            logger.warning(f"Healthcheck Redis probe error: {e}")
            redis_status = f"error: {str(e)}"
    else:
        redis_status = "ok (locmem)"

    is_healthy = db_status == "ok" and (redis_status.startswith("ok"))
    status_code = 200 if is_healthy else 503

    return JsonResponse({
        "status": "healthy" if is_healthy else "unhealthy",
        "service": "hi-bel",
        "version": getattr(settings, "MCP_SERVER_VERSION", "0.1.0"),
        "mcp_gateway": "active",
        "isolation_mode": "strict_mcp_only",
        "checks": {
            "database": db_status,
            "redis": redis_status,
        }
    }, status=status_code)

urlpatterns = [
    path("healthz", health_check, name="healthz_short"),
    path("healthz/", health_check, name="healthz"),
    path("health/", health_check, name="health_check"),
    path("api/health/", health_check, name="api_health_check"),
    path("api/health", health_check, name="api_health_short"),
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

