import asyncio
from django.core.management.base import BaseCommand
from apps.mcp_server.server import mcp_server_instance

class Command(BaseCommand):
    help = "Run the hi-bel Model Context Protocol (MCP) server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--transport",
            type=str,
            default="stdio",
            choices=["stdio", "sse"],
            help="Transport mode (stdio or sse)",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Port for SSE standalone server",
        )

    def handle(self, *args, **options):
        transport = options["transport"]
        self.stdout.write(self.style.SUCCESS(f"Starting hi-bel MCP Server via {transport}..."))

        if transport == "stdio":
            asyncio.run(mcp_server_instance.run_stdio_async())
        else:
            port = options["port"]
            asyncio.run(mcp_server_instance.run_sse_async(port=port))
