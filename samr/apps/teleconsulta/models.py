"""Modelos de la app teleconsulta."""
from django.conf import settings
from django.db import models

from core.models import ModeloBase
from apps.triaje.models import SolicitudAtencion


class EstadoTeleconsulta:
    """Estados posibles de una teleconsulta."""

    PROGRAMADA = "PROGRAMADA"
    EN_CURSO = "EN_CURSO"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"

    CHOICES = (
        (PROGRAMADA, "Programada"),
        (EN_CURSO, "En curso"),
        (FINALIZADA, "Finalizada"),
        (CANCELADA, "Cancelada"),
    )


class Teleconsulta(ModeloBase):
    """Consulta medica remota entre un medico y un paciente."""

    codigo = models.CharField("Codigo", max_length=20, unique=True)
    solicitud = models.ForeignKey(
        SolicitudAtencion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teleconsultas",
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teleconsultas_como_medico",
    )
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teleconsultas_como_paciente",
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=EstadoTeleconsulta.CHOICES,
        default=EstadoTeleconsulta.PROGRAMADA,
    )
    fecha_programada = models.DateTimeField("Fecha programada")
    enlace_sala = models.URLField("Enlace de sala virtual", blank=True)
    motivo = models.CharField("Motivo", max_length=200)
    diagnostico = models.TextField("Diagnostico", blank=True)
    notas = models.TextField("Notas de la consulta", blank=True)

    class Meta:
        verbose_name = "Teleconsulta"
        verbose_name_plural = "Teleconsultas"
        ordering = ["-fecha_programada"]

    def __str__(self):
        return "{0} - {1}".format(self.codigo, self.estado)

    @property
    def esta_finalizada(self):
        return self.estado == EstadoTeleconsulta.FINALIZADA


class Receta(ModeloBase):
    """Receta medica emitida en el marco de una teleconsulta."""

    codigo = models.CharField("Codigo", max_length=20, unique=True)
    teleconsulta = models.OneToOneField(
        Teleconsulta,
        on_delete=models.CASCADE,
        related_name="receta",
    )
    indicaciones_generales = models.TextField("Indicaciones generales", blank=True)
    leida = models.BooleanField("Leída por el paciente", default=False)

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        ordering = ["-creado_en"]

    def __str__(self):
        return "Receta {0}".format(self.codigo)


class DetalleReceta(ModeloBase):
    """Cada medicamento prescrito dentro de una receta."""

    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    medicamento = models.CharField("Medicamento", max_length=150)
    dosis = models.CharField("Dosis", max_length=80)
    frecuencia = models.CharField("Frecuencia", max_length=80)
    duracion = models.CharField("Duracion", max_length=80)

    class Meta:
        verbose_name = "Detalle de receta"
        verbose_name_plural = "Detalles de receta"
        ordering = ["id"]

    def __str__(self):
        return "{0} ({1})".format(self.medicamento, self.dosis)


class HistorialClinico(ModeloBase):
    """Entrada del historial clinico de un paciente."""

    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="historial_clinico",
    )
    teleconsulta = models.ForeignKey(
        Teleconsulta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entradas_historial",
    )
    descripcion = models.TextField("Descripcion")
    diagnostico = models.TextField("Diagnostico", blank=True)

    class Meta:
        verbose_name = "Historial clinico"
        verbose_name_plural = "Historiales clinicos"
        ordering = ["-creado_en"]

    def __str__(self):
        return "Historial de {0} ({1})".format(
            self.paciente.nombre_completo, self.creado_en.date()
        )
