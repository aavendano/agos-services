from django.urls import path
from .views import MCPInfoView

urlpatterns = [
    path("", MCPInfoView.as_view(), name="mcp_info"),
]
