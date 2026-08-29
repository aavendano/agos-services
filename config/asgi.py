import os
from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django ASGI application early to ensure models are loaded
django_asgi_app = get_asgi_application()

# Import MCP Starlette routes
from apps.mcp_server.transport import get_starlette_routes

routes = [
    *get_starlette_routes(),
    Mount("/", django_asgi_app),
]

application = Starlette(
    routes=routes,
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        )
    ],
)
