from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MCPClientViewSet, ToolPermissionViewSet

router = DefaultRouter()
router.register(r"clients", MCPClientViewSet, basename="mcp-client")
router.register(r"permissions", ToolPermissionViewSet, basename="tool-permission")

urlpatterns = [
    path("", include(router.urls)),
]
