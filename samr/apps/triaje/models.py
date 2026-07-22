"""Modelos de la app triaje."""
from django.conf import settings
from django.db import models

from core.models import ModeloBase


class EstadoSolicitud:
    """Estados posibles de una solicitud de atencion."""

    PENDIENTE = "PENDIENTE"
    EN_TRIAJE = "EN_TRIAJE"
    ATENDIDA = "ATENDIDA"
    CANCELADA = "CANCELADA"

    CHOICES = (
        (PENDIENTE, "Pendiente"),
        (EN_TRIAJE, "En triaje"),
        (ATENDIDA, "Atendida"),
        (CANCELADA, "Cancelada"),
    )


class NivelUrgencia:
    """Niveles de urgencia segun evaluacion de triaje (escala tipo Manchester)."""

    EMERGENCIA = 1
    MUY_URGENTE = 2
    URGENTE = 3
    NORMAL = 4
    NO_URGENTE = 5

    CHOICES = (
        (EMERGENCIA, "Emergencia"),
        (MUY_URGENTE, "Muy urgente"),
        (URGENTE, "Urgente"),
        (NORMAL, "Normal"),
        (NO_URGENTE, "No urgente"),
    )


class SolicitudAtencion(ModeloBase):
    """Solicitud de atencion medica creada por un paciente."""

    codigo = models.CharField("Codigo", max_length=20, unique=True)
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitudes",
    )
    motivo = models.CharField("Motivo", max_length=200)
    sintomas = models.TextField("Sintomas")
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=EstadoSolicitud.CHOICES,
        default=EstadoSolicitud.PENDIENTE,
    )

    class Meta:
        verbose_name = "Solicitud de atencion"
        verbose_name_plural = "Solicitudes de atencion"
        ordering = ["-creado_en"]

    def __str__(self):
        return "{0} - {1} ({2})".format(self.codigo, self.motivo, self.estado)

    @property
    def esta_pendiente(self):
        return self.estado == EstadoSolicitud.PENDIENTE

    @property
    def esta_cerrada(self):
        return self.estado in (EstadoSolicitud.ATENDIDA, EstadoSolicitud.CANCELADA)


class EvaluacionTriaje(ModeloBase):
    """Evaluacion de urgencia asociada a una solicitud de atencion."""

    solicitud = models.OneToOneField(
        SolicitudAtencion,
        on_delete=models.CASCADE,
        related_name="evaluacion",
    )
    evaluado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triajes_realizados",
    )
    nivel_urgencia = models.PositiveSmallIntegerField(
        "Nivel de urgencia",
        choices=NivelUrgencia.CHOICES,
        default=NivelUrgencia.NORMAL,
    )
    observaciones = models.TextField("Observaciones", blank=True)
    temperatura = models.DecimalField(
        "Temperatura (C)", max_digits=4, decimal_places=1, null=True, blank=True
    )
    frecuencia_cardiaca = models.PositiveIntegerField(
        "Frecuencia cardiaca (lpm)", null=True, blank=True
    )

    class Meta:
        verbose_name = "Evaluacion de triaje"
        verbose_name_plural = "Evaluaciones de triaje"
        ordering = ["nivel_urgencia", "-creado_en"]

    def __str__(self):
        return "Triaje {0} - nivel {1}".format(
            self.solicitud.codigo, self.nivel_urgencia
        )

    @property
    def es_critica(self):
        return self.nivel_urgencia in (
            NivelUrgencia.EMERGENCIA,
            NivelUrgencia.MUY_URGENTE,
        )


class MensajeChat(ModeloBase):
    """Mensaje de chat conversacional en triaje."""
    solicitud = models.ForeignKey(
        SolicitudAtencion,
        on_delete=models.CASCADE,
        related_name="mensajes"
    )
    autor = models.CharField("Autor", max_length=10, choices=(("PACIENTE", "Paciente"), ("BOT", "Bot")))
    texto = models.TextField("Texto del mensaje")

    class Meta:
        verbose_name = "Mensaje de chat"
        verbose_name_plural = "Mensajes de chat"
        ordering = ["creado_en"]

    def __str__(self):
        return f"{self.autor} - {self.solicitud.codigo}"
