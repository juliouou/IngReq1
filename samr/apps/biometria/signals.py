"""Signals de la app biometria: alertas y emision por WebSocket."""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.biometria.models import LecturaBiometrica
from apps.biometria.services import generar_alerta_desde_lectura

logger = logging.getLogger("samr")


@receiver(post_save, sender=LecturaBiometrica)
def procesar_lectura(sender, instance, created, **kwargs):
    """
    Al crear una lectura fuera de rango:
    genera la alerta y la emite por el canal WebSocket del paciente.
    """
    if not created:
        return

    alerta = generar_alerta_desde_lectura(instance)
    if alerta is None:
        return

    logger.info(
        "Alerta %s generada para paciente %s",
        alerta.nivel,
        alerta.paciente_id,
    )

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    grupo = "biometria_{0}".format(alerta.paciente_id)
    try:
        async_to_sync(channel_layer.group_send)(
            grupo,
            {
                "type": "alerta_biometrica",
                "data": {
                    "alerta_id": alerta.id,
                    "nivel": alerta.nivel,
                    "mensaje": alerta.mensaje,
                    "lectura_id": instance.id,
                    "tipo_signo": instance.tipo_signo,
                    "valor": str(instance.valor),
                },
            },
        )
    except Exception:  # noqa: BLE001
        logger.debug("No se pudo emitir la alerta por WebSocket", exc_info=True)
