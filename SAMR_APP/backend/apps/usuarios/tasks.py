"""Tareas asincronas de la app usuarios (Celery)."""
import logging

from celery import shared_task

logger = logging.getLogger("samr")


@shared_task
def enviar_correo_bienvenida(usuario_id):
    """Simula el envio de un correo de bienvenida (ejecucion eager en dev)."""
    from apps.usuarios.models import Usuario

    usuario = Usuario.objects.filter(pk=usuario_id).first()
    if usuario is None:
        return "usuario_inexistente"
    logger.info("Correo de bienvenida simulado enviado a %s", usuario.email)
    return "ok"
