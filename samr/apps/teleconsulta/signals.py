"""Signals de la app teleconsulta."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.teleconsulta.models import Teleconsulta

logger = logging.getLogger("samr")


@receiver(post_save, sender=Teleconsulta)
def registrar_creacion_teleconsulta(sender, instance, created, **kwargs):
    """Deja traza en el log al agendar una teleconsulta."""
    if created:
        logger.info(
            "Teleconsulta %s agendada (medico=%s, paciente=%s)",
            instance.codigo,
            instance.medico_id,
            instance.paciente_id,
        )
