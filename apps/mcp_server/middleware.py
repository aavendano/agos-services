import uuid
import logging
from typing import Optional, Tuple
from asgiref.sync import sync_to_async
from django.conf import settings
from apps.channels.models import MCPClient, ToolPermission

logger = logging.getLogger(__name__)

class PermissionDeniedError(Exception):
    """Raised when an MCP client lacks authorization to execute a tool."""
    pass

class AuthenticationRequiredError(Exception):
    """Raised when an unauthenticated or invalid client attempts MCP access."""
    pass

class PrivilegeGate:
    """
    Strict privilege gateway enforcing MCPClient authentication and ToolPermission authorization.
    Every tool call from external applications MUST pass through this gate.
    """
    @staticmethod
    async def authenticate_token(token_str: Optional[str]) -> MCPClient:
        if not getattr(settings, "MCP_AUTH_REQUIRED", True):
            # Development bypass only if explicitly disabled
            client = await sync_to_async(lambda: MCPClient.objects.filter(is_active=True).first())()
            if client:
                return client
            client = await sync_to_async(lambda: MCPClient.objects.create(name="Dev Client", is_active=True))()
            return client

        if not token_str:
            raise AuthenticationRequiredError("Missing client authorization token. Provide 'Authorization: Bearer <TOKEN>' or '?token=<TOKEN>'.")

        # Clean token
        if token_str.lower().startswith("bearer "):
            token_str = token_str[7:].strip()

        try:
            token_uuid = uuid.UUID(token_str)
        except (ValueError, AttributeError):
            raise AuthenticationRequiredError("Invalid client token format. UUID required.")

        client = await sync_to_async(
            lambda: MCPClient.objects.filter(token=token_uuid, is_active=True).first()
        )()

        if not client:
            raise AuthenticationRequiredError("Client authentication failed. Token does not exist or client is deactivated.")

        return client

    @staticmethod
    async def verify_tool_permission(client: MCPClient, tool_name: str) -> bool:
        """Checks if the authenticated client is granted permission to invoke tool_name."""
        has_perm = await sync_to_async(
            lambda: ToolPermission.objects.filter(client=client, tool_name=tool_name, allowed=True).exists()
        )()

        if not has_perm:
            logger.warning(f"Access Denied: Client '{client.name}' ({client.token}) attempted to call unauthorized tool '{tool_name}'")
            raise PermissionDeniedError(
                f"Permission Denied: Client '{client.name}' is not authorized to invoke tool '{tool_name}'."
            )

        return True
