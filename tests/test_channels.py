import pytest
import uuid
from apps.channels.models import MCPClient, ToolPermission

@pytest.mark.django_db
class TestChannelsAndPermissions:
    def test_create_mcp_client(self):
        client = MCPClient.objects.create(name="Cursor Agent")
        assert client.name == "Cursor Agent"
        assert isinstance(client.token, uuid.UUID)
        assert client.is_active is True
        assert client.rate_limit_rpm == 60

    def test_tool_permission_logic(self, active_mcp_client):
        assert active_mcp_client.has_permission_for_tool("get_products") is True
        assert active_mcp_client.has_permission_for_tool("get_product_by_id") is True
        assert active_mcp_client.has_permission_for_tool("create_draft_order") is False
        assert active_mcp_client.has_permission_for_tool("non_existent_tool") is False

    def test_inactive_client_denied(self, inactive_mcp_client):
        assert inactive_mcp_client.has_permission_for_tool("get_products") is False

    def test_unique_client_tool_permission(self, active_mcp_client):
        with pytest.raises(Exception):
            ToolPermission.objects.create(
                client=active_mcp_client,
                tool_name="get_products",
                allowed=True,
            )
