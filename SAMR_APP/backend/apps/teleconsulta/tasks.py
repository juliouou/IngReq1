"""Tareas asincronas de la app teleconsulta (Celery)."""
import logging

from celery import shared_task

logger = logging.getLogger("samr")


@shared_task
def recordar_teleconsultas_programadas():
    """Cuenta las teleconsultas programadas (tarea demostrativa)."""
    from apps.teleconsulta.models import EstadoTeleconsulta, Teleconsulta

    total = Teleconsulta.objects.filter(
        estado=EstadoTeleconsulta.PROGRAMADA
    ).count()
    logger.info("Teleconsultas programadas: %s", total)
    return total
