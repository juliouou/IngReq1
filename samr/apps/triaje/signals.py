"""Signals de la app triaje."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.triaje.models import EvaluacionTriaje

logger = logging.getLogger("samr")


@receiver(post_save, sender=EvaluacionTriaje)
def notificar_triaje_critico(sender, instance, created, **kwargs):
    """Registra en el log cuando se crea una evaluacion critica."""
    if created and instance.es_critica:
        logger.warning(
            "Triaje CRITICO para solicitud %s (nivel %s)",
            instance.solicitud.codigo,
            instance.nivel_urgencia,
        )
