"""Punto de entrada ASGI para el proyecto SAMR (HTTP + WebSocket)."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# La app ASGI de Django debe inicializarse antes de importar consumers/rutas
# que dependan de modelos ya cargados.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from apps.biometria.routing import websocket_urlpatterns as biometria_ws  # noqa: E402
from apps.teleconsulta.routing import websocket_urlpatterns as teleconsulta_ws  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(biometria_ws + teleconsulta_ws)),
    }
)
