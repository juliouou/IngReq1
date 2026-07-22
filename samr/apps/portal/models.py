"""Modelos de la app portal: soporte de MFA y consentimiento LOPDP.

Estos modelos son el equivalente a "ServicioMFA" y "ConsentimientoLOPDP" del
diagrama de secuencia UC-01 -- ServicioMFA no tiene tabla propia porque es un
sistema externo (regla 7 del proyecto: se pliega como llamada reflexiva),
pero necesitamos persistir el codigo generado para poder validarlo despues.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import ModeloBase


class CodigoMFA(ModeloBase):
    """RF-03: codigo de un solo uso para autenticacion multifactor."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="codigos_mfa"
    )
    codigo = models.CharField("Codigo", max_length=6)
    expira_en = models.DateTimeField("Expira en")
    intentos = models.PositiveSmallIntegerField("Intentos", default=0)
    usado = models.BooleanField("Usado", default=False)

    class Meta:
        verbose_name = "Codigo MFA"
        verbose_name_plural = "Codigos MFA"
        ordering = ["-creado_en"]

    def __str__(self):
        return "MFA {0} ({1})".format(self.usuario.email, "usado" if self.usado else "activo")

    @property
    def expirado(self):
        return timezone.now() > self.expira_en


class ConsentimientoLOPDP(ModeloBase):
    """RF-18: registro de consentimiento explicito bajo la LOPDP."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consentimiento_lopdp"
    )
    activo = models.BooleanField("Activo", default=False)
    version_politica = models.CharField("Version de politica", max_length=10, default="1.0")
    ip = models.GenericIPAddressField("Direccion IP", null=True, blank=True)
    aceptado_en = models.DateTimeField("Aceptado en", null=True, blank=True)

    class Meta:
        verbose_name = "Consentimiento LOPDP"
        verbose_name_plural = "Consentimientos LOPDP"
        ordering = ["-creado_en"]

    def __str__(self):
        return "Consentimiento de {0}: {1}".format(
            self.usuario.email, "activo" if self.activo else "inactivo"
        )
