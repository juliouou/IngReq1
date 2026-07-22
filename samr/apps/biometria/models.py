"""Modelos de la app biometria."""
from django.conf import settings
from django.db import models

from core.models import ModeloBase


class TipoDispositivo:
    """Tipos de dispositivo IoT soportados."""

    PULSERA = "PULSERA"
    OXIMETRO = "OXIMETRO"
    TENSIOMETRO = "TENSIOMETRO"
    TERMOMETRO = "TERMOMETRO"
    GLUCOMETRO = "GLUCOMETRO"

    CHOICES = (
        (PULSERA, "Pulsera inteligente"),
        (OXIMETRO, "Oximetro"),
        (TENSIOMETRO, "Tensiometro"),
        (TERMOMETRO, "Termometro"),
        (GLUCOMETRO, "Glucometro"),
    )


class TipoSigno:
    """Tipos de signo vital medidos por los dispositivos."""

    FRECUENCIA_CARDIACA = "FRECUENCIA_CARDIACA"
    SATURACION_OXIGENO = "SATURACION_OXIGENO"
    PRESION_SISTOLICA = "PRESION_SISTOLICA"
    PRESION_DIASTOLICA = "PRESION_DIASTOLICA"
    TEMPERATURA = "TEMPERATURA"
    GLUCOSA = "GLUCOSA"

    CHOICES = (
        (FRECUENCIA_CARDIACA, "Frecuencia cardiaca (lpm)"),
        (SATURACION_OXIGENO, "Saturacion de oxigeno (%)"),
        (PRESION_SISTOLICA, "Presion sistolica (mmHg)"),
        (PRESION_DIASTOLICA, "Presion diastolica (mmHg)"),
        (TEMPERATURA, "Temperatura (C)"),
        (GLUCOSA, "Glucosa (mg/dL)"),
    )

    # Rangos normales de referencia (minimo, maximo) por tipo de signo.
    RANGOS = {
        FRECUENCIA_CARDIACA: (60, 100),
        SATURACION_OXIGENO: (95, 100),
        PRESION_SISTOLICA: (90, 120),
        PRESION_DIASTOLICA: (60, 80),
        TEMPERATURA: (36, 37.5),
        GLUCOSA: (70, 140),
    }


class NivelAlerta:
    """Niveles de severidad de una alerta biometrica."""

    INFO = "INFO"
    ADVERTENCIA = "ADVERTENCIA"
    CRITICA = "CRITICA"

    CHOICES = (
        (INFO, "Informativa"),
        (ADVERTENCIA, "Advertencia"),
        (CRITICA, "Critica"),
    )


class DispositivoIoT(ModeloBase):
    """Dispositivo IoT asignado a un paciente."""

    codigo = models.CharField("Codigo", max_length=20, unique=True)
    nombre = models.CharField("Nombre", max_length=120)
    tipo = models.CharField("Tipo", max_length=20, choices=TipoDispositivo.CHOICES)
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dispositivos",
    )
    numero_serie = models.CharField("Numero de serie", max_length=60, unique=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Dispositivo IoT"
        verbose_name_plural = "Dispositivos IoT"
        ordering = ["-creado_en"]

    def __str__(self):
        return "{0} ({1})".format(self.nombre, self.codigo)


class LecturaBiometrica(ModeloBase):
    """Lectura de un signo vital enviada por un dispositivo IoT."""

    dispositivo = models.ForeignKey(
        DispositivoIoT,
        on_delete=models.CASCADE,
        related_name="lecturas",
    )
    tipo_signo = models.CharField(
        "Tipo de signo", max_length=30, choices=TipoSigno.CHOICES
    )
    valor = models.DecimalField("Valor", max_digits=6, decimal_places=2)
    unidad = models.CharField("Unidad", max_length=10, blank=True)
    fuera_de_rango = models.BooleanField("Fuera de rango", default=False)
    tomada_en = models.DateTimeField("Tomada en", auto_now_add=True)

    class Meta:
        verbose_name = "Lectura biometrica"
        verbose_name_plural = "Lecturas biometricas"
        ordering = ["-tomada_en"]
        indexes = [
            models.Index(fields=["dispositivo", "tipo_signo"]),
        ]

    def __str__(self):
        return "{0}={1} ({2})".format(self.tipo_signo, self.valor, self.unidad)

    def evaluar_rango(self):
        """Determina si la lectura esta fuera del rango normal de referencia."""
        rango = TipoSigno.RANGOS.get(self.tipo_signo)
        if not rango:
            return False
        minimo, maximo = rango
        return not (minimo <= float(self.valor) <= maximo)


class Alerta(ModeloBase):
    """Alerta generada a partir de una lectura fuera de rango."""

    lectura = models.ForeignKey(
        LecturaBiometrica,
        on_delete=models.CASCADE,
        related_name="alertas",
    )
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alertas",
    )
    nivel = models.CharField(
        "Nivel", max_length=20, choices=NivelAlerta.CHOICES, default=NivelAlerta.INFO
    )
    mensaje = models.CharField("Mensaje", max_length=255)
    atendida = models.BooleanField("Atendida", default=False)

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ["-creado_en"]

    def __str__(self):
        return "[{0}] {1}".format(self.nivel, self.mensaje)
