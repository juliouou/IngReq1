"""Signals de la app usuarios: creacion automatica de perfiles por rol."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from shared.constants import Roles
from shared.utils import generar_codigo
from apps.usuarios.models import PerfilMedico, PerfilPaciente, Usuario


@receiver(post_save, sender=Usuario)
def crear_perfil_por_rol(sender, instance, created, **kwargs):
    """Al crear un usuario, genera el perfil que corresponde a su rol."""
    if not created:
        return

    if instance.rol == Roles.PACIENTE:
        PerfilPaciente.objects.get_or_create(usuario=instance)
    elif instance.rol == Roles.MEDICO:
        PerfilMedico.objects.get_or_create(
            usuario=instance,
            defaults={
                "especialidad": "Medicina General",
                "numero_registro": generar_codigo("MED-", 6),
            },
        )
