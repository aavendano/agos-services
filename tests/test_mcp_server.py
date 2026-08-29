import pytest
import uuid
from apps.mcp_server.middleware import PrivilegeGate, AuthenticationRequiredError, PermissionDeniedError
from apps.mcp_server.tools import handle_get_products, handle_create_draft_order

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestMCPServerPrivilegeGate:
    async def test_missing_token_raises_auth_required(self):
        with pytest.raises(AuthenticationRequiredError):
            await PrivilegeGate.authenticate_token(None)

    async def test_invalid_uuid_token_raises_auth_required(self):
        with pytest.raises(AuthenticationRequiredError):
            await PrivilegeGate.authenticate_token("invalid-uuid-string")

    async def test_non_existent_token_raises_auth_required(self):
        random_uuid = str(uuid.uuid4())
        with pytest.raises(AuthenticationRequiredError):
            await PrivilegeGate.authenticate_token(random_uuid)

    async def test_valid_token_returns_client(self, active_mcp_client):
        client = await PrivilegeGate.authenticate_token(str(active_mcp_client.token))
        assert client.id == active_mcp_client.id

    async def test_bearer_prefix_parsed_successfully(self, active_mcp_client):
        client = await PrivilegeGate.authenticate_token(f"Bearer {active_mcp_client.token}")
        assert client.id == active_mcp_client.id

    async def test_permission_denied_for_unauthorized_tool(self, active_mcp_client):
        with pytest.raises(PermissionDeniedError):
            await PrivilegeGate.verify_tool_permission(active_mcp_client, "create_draft_order")

    async def test_permission_granted_for_authorized_tool(self, active_mcp_client):
        allowed = await PrivilegeGate.verify_tool_permission(active_mcp_client, "get_products")
        assert allowed is True

    async def test_handle_create_draft_order_enforces_gate(self, active_mcp_client):
        with pytest.raises(PermissionDeniedError):
            await handle_create_draft_order(
                client=active_mcp_client,
                line_items=[{"variant_id": "1", "quantity": 1}],
            )
