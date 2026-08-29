import json
import logging
from typing import List
from starlette.routing import Route
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from mcp.server.sse import SseServerTransport
from apps.mcp_server.server import mcp_server_instance
from apps.mcp_server.middleware import PrivilegeGate, AuthenticationRequiredError, PermissionDeniedError

logger = logging.getLogger(__name__)

sse_transport = SseServerTransport("/mcp/messages/")

async def sse_endpoint(request: Request):
    """
    SSE Endpoint for external MCP clients (Cursor, Claude Desktop, Antigravity).
    Authenticates client token from Authorization header or 'token' query param.
    """
    auth_header = request.headers.get("authorization")
    token_param = request.query_params.get("token") or request.headers.get("x-mcp-client-token")
    token = auth_header or token_param

    try:
        client = await PrivilegeGate.authenticate_token(token)
    except AuthenticationRequiredError as auth_err:
        return JSONResponse(
            {"error": "Unauthorized", "detail": str(auth_err)},
            status_code=401,
        )

    logger.info(f"MCP client connected via SSE: {client.name} (token: {client.token})")

    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_server_instance.run(
            read_stream,
            write_stream,
            mcp_server_instance.create_initialization_options(),
        )
    return Response()


async def messages_endpoint(request: Request):
    """
    Message endpoint for SSE transport messages (JSON-RPC requests from client).
    """
    return await sse_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


def get_starlette_routes() -> List[Route]:
    return [
        Route("/mcp/sse", endpoint=sse_endpoint, methods=["GET"]),
        Route("/mcp/messages/", endpoint=messages_endpoint, methods=["POST"]),
        Route("/mcp/messages", endpoint=messages_endpoint, methods=["POST"]),
    ]
