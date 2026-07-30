"""Consumers WebSocket para senalización WebRTC en teleconsulta."""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class SenalizacionConsumer(AsyncWebsocketConsumer):
    """Consumer para la señalización WebRTC entre médico y paciente."""

    @database_sync_to_async
    def obtener_teleconsulta(self, teleconsulta_id, user):
        from apps.teleconsulta.models import Teleconsulta
        try:
            tc = Teleconsulta.objects.select_related("medico", "paciente").get(id=teleconsulta_id)
            if user == tc.medico or user == tc.paciente:
                return tc
        except Teleconsulta.DoesNotExist:
            pass
        return None

    @database_sync_to_async
    def registrar_auditoria(self, user, accion, teleconsulta_id):
        from apps.auditoria.services import RegistroAuditoriaService
        try:
            RegistroAuditoriaService().registrar(
                usuario=user,
                accion=accion,
                ruta=f"/ws/teleconsulta/{teleconsulta_id}/signaling/",
                codigo_estado=200,
            )
        except Exception as e:
            logger.warning(f"Error al registrar auditoría en WebRTC: {e}")

    async def connect(self):
        self.teleconsulta_id = self.scope["url_route"]["kwargs"]["teleconsulta_id"]
        self.room_group_name = f"teleconsulta_{self.teleconsulta_id}"
        self.user = self.scope.get("user")

        if not self.user or self.user.is_anonymous:
            logger.warning(f"Intento de conexión WebRTC sin autenticar en teleconsulta {self.teleconsulta_id}")
            await self.close()
            return

        tc = await self.obtener_teleconsulta(self.teleconsulta_id, self.user)
        if not tc:
            logger.warning(f"Usuario {self.user.email} no autorizado para teleconsulta {self.teleconsulta_id}")
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.registrar_auditoria(self.user, "WEBRTC_CONEXION", self.teleconsulta_id)
        logger.info(f"Usuario {self.user.email} conectado a la señalización WebRTC en {self.room_group_name}")

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            if hasattr(self, "user") and self.user and not self.user.is_anonymous:
                await self.registrar_auditoria(self.user, "WEBRTC_DESCONEXION", self.teleconsulta_id)
                logger.info(f"Usuario {self.user.email} desconectado de la señalización WebRTC en {self.room_group_name}")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "senales_webrtc",
                    "message": text_data,
                    "sender_channel_name": self.channel_name,
                },
            )

    async def senales_webrtc(self, event):
        if event["sender_channel_name"] != self.channel_name:
            await self.send(text_data=event["message"])
