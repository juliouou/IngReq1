"""Rutas WebSocket de la app biometria (Channels)."""
from django.urls import re_path

from apps.biometria.consumers import MonitoreoConsumer

websocket_urlpatterns = [
    re_path(
        r"^ws/biometria/(?P<paciente_id>\d+)/$",
        MonitoreoConsumer.as_asgi(),
    ),
]
