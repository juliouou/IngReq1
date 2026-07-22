"""Tareas asincronas de la app biometria (Celery)."""
import logging

from celery import shared_task

logger = logging.getLogger("samr")


@shared_task
def resumen_alertas_pendientes():
    """Cuenta las alertas no atendidas (tarea demostrativa)."""
    from apps.biometria.models import Alerta

    total = Alerta.objects.filter(atendida=False).count()
    logger.info("Alertas pendientes: %s", total)
    return total
