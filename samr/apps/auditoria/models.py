"""Modelos de la app auditoria."""
from django.conf import settings
from django.db import models

from core.models import ModeloBase


class RegistroAuditoria(ModeloBase):
    """
    Registro de una accion que modifica datos en el sistema.

    Lo crea automaticamente core.middleware.AuditoriaMiddleware en cada
    peticion POST/PUT/PATCH/DELETE de un usuario autenticado.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros_auditoria",
    )
    accion = models.CharField("Accion (metodo HTTP)", max_length=10)
    ruta = models.CharField("Ruta", max_length=255)
    codigo_estado = models.PositiveIntegerField("Codigo de estado HTTP")
    request_id = models.CharField("ID de peticion", max_length=40, blank=True)
    ip = models.GenericIPAddressField("Direccion IP", null=True, blank=True)

    class Meta:
        verbose_name = "Registro de auditoria"
        verbose_name_plural = "Registros de auditoria"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["usuario", "accion"]),
            models.Index(fields=["creado_en"]),
        ]

    def __str__(self):
        etiqueta_usuario = self.usuario.email if self.usuario else "anonimo"
        return "{0} {1} {2} -> {3}".format(
            etiqueta_usuario, self.accion, self.ruta, self.codigo_estado
        )
