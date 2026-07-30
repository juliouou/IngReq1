"""Modelos de la app auditoria."""
import hashlib

from django.conf import settings
from django.db import models

from shared.models import ModeloBase


class RegistroAuditoria(ModeloBase):
    """
    Registro de una accion que modifica datos en el sistema.

    Se sigue pudiendo crear de forma generica (metodo HTTP + ruta, como
    hace core.middleware.AuditoriaMiddleware en cada POST/PUT/PATCH/DELETE),
    pero ahora tambien admite registrar la accion de NEGOCIO concreta
    (entidad + estado anterior/nuevo), que es lo que de verdad permite
    responder "que cambio, de que valor a que valor y quien lo hizo" --
    algo indispensable al auditar datos clinicos.

    Ademas, cada registro queda encadenado por hash SHA-256 al anterior
    (ver calcular_hash/save): si alguien edita o borra una fila directamente
    en la base de datos, la cadena se rompe y es detectable.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros_auditoria",
    )
    # Campos originales (metodo HTTP). Se mantienen para no romper a los
    # callers existentes (middleware, seed, vistas web).
    accion = models.CharField("Accion", max_length=50)
    ruta = models.CharField("Ruta", max_length=255, blank=True, default="")
    codigo_estado = models.PositiveIntegerField(
        "Codigo de estado HTTP", null=True, blank=True
    )
    request_id = models.CharField("ID de peticion", max_length=40, blank=True)
    ip = models.GenericIPAddressField("Direccion IP", null=True, blank=True)

    # Campos nuevos: accion de negocio sobre una entidad concreta.
    entidad = models.CharField("Entidad afectada", max_length=100, blank=True)
    entidad_id = models.CharField("ID de la entidad", max_length=64, blank=True)
    estado_anterior = models.JSONField("Estado anterior", null=True, blank=True)
    estado_nuevo = models.JSONField("Estado nuevo", null=True, blank=True)

    # Cadena de hashes (integridad / a prueba de manipulacion).
    hash_anterior = models.CharField(max_length=64, blank=True)
    hash_actual = models.CharField(max_length=64, editable=False, blank=True)

    class Meta:
        verbose_name = "Registro de auditoria"
        verbose_name_plural = "Registros de auditoria"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["usuario", "accion"]),
            models.Index(fields=["creado_en"]),
            models.Index(fields=["entidad", "entidad_id"]),
        ]

    def calcular_hash(self):
        contenido = "{0}{1}{2}{3}{4}{5}".format(
            self.hash_anterior,
            self.entidad,
            self.entidad_id,
            self.accion,
            self.estado_anterior,
            self.estado_nuevo,
        )
        return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    def save(self, *args, **kwargs):
        if not self.hash_actual:
            ultimo = RegistroAuditoria.objects.order_by("-creado_en", "-id").first()
            self.hash_anterior = ultimo.hash_actual if ultimo else ""
            self.hash_actual = self.calcular_hash()
        super().save(*args, **kwargs)

    def __str__(self):
        etiqueta_usuario = self.usuario.email if self.usuario else "anonimo"
        if self.entidad:
            return "{0} {1} {2}#{3}".format(
                etiqueta_usuario, self.accion, self.entidad, self.entidad_id
            )
        return "{0} {1} {2} -> {3}".format(
            etiqueta_usuario, self.accion, self.ruta, self.codigo_estado
        )
