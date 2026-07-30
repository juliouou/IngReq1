"""Consumers WebSocket de la app biometria."""
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class MonitoreoConsumer(AsyncWebsocketConsumer):
    """
    Canal de monitoreo en tiempo real por paciente.

    El cliente se conecta a /ws/biometria/<paciente_id>/ y recibe los
    eventos de alerta emitidos al grupo correspondiente.
    """

    async def connect(self):
        self.paciente_id = self.scope["url_route"]["kwargs"]["paciente_id"]
        self.grupo = "biometria_{0}".format(self.paciente_id)
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            "tipo": "conexion",
            "mensaje": "Monitoreo activo para paciente {0}".format(self.paciente_id),
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.grupo, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Responde a un ping simple para verificar el canal."""
        try:
            data = json.loads(text_data) if text_data else {}
        except json.JSONDecodeError:
            data = {}
        if data.get("tipo") == "ping":
            await self.send(text_data=json.dumps({"tipo": "pong"}))

    async def alerta_biometrica(self, event):
        """Handler del evento enviado con type='alerta_biometrica'."""
        await self.send(text_data=json.dumps({
            "tipo": "alerta",
            "data": event.get("data", {}),
        }))
