"""Rutas WebSocket para teleconsulta."""
from django.urls import re_path
from apps.teleconsulta.consumers import SenalizacionConsumer

websocket_urlpatterns = [
    re_path(
        r"^ws/teleconsulta/(?P<teleconsulta_id>\d+)/signaling/$",
        SenalizacionConsumer.as_asgi(),
    ),
]
