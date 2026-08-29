from django.http import JsonResponse
from django.views import View

class MCPInfoView(View):
    """Informational endpoint explaining that external access is exclusively via MCP protocol."""
    def get(self, request):
        return JsonResponse({
            "service": "bel-agents MCP Gateway",
            "protocol": "Model Context Protocol (MCP) 2024-11-05 / 2.x",
            "isolation_policy": "Strict MCP only - No direct external REST bypass",
            "transport_endpoints": {
                "sse": "/mcp/sse",
                "messages": "/mcp/messages/",
            },
            "authentication": "Bearer token or X-MCP-Client-Token header required",
            "available_tools": [
                "get_products",
                "get_product_by_id",
                "search_inventory",
                "get_orders",
                "get_order_by_id",
                "create_draft_order",
            ]
        })
