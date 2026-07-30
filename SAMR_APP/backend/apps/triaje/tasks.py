"""Tareas asincronas de la app triaje (Celery)."""
import logging

from celery import shared_task

logger = logging.getLogger("samr")


@shared_task
def recalcular_prioridades():
    """Tarea de mantenimiento: cuenta solicitudes pendientes (demostrativa)."""
    from apps.triaje.models import EstadoSolicitud, SolicitudAtencion

    total = SolicitudAtencion.objects.filter(
        estado=EstadoSolicitud.PENDIENTE
    ).count()
    logger.info("Solicitudes pendientes: %s", total)
    return total
