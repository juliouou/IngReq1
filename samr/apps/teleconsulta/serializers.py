"""Serializers de la app teleconsulta."""
from rest_framework import serializers

from apps.teleconsulta.models import (
    DetalleReceta,
    HistorialClinico,
    Receta,
    Teleconsulta,
)


class DetalleRecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleReceta
        fields = ("id", "medicamento", "dosis", "frecuencia", "duracion")
        read_only_fields = ("id",)


class RecetaSerializer(serializers.ModelSerializer):
    detalles = DetalleRecetaSerializer(many=True, read_only=True)

    class Meta:
        model = Receta
        fields = (
            "id", "codigo", "teleconsulta", "indicaciones_generales",
            "detalles", "creado_en",
        )
        read_only_fields = ("id", "codigo", "creado_en")


class TeleconsultaSerializer(serializers.ModelSerializer):
    medico_nombre = serializers.CharField(
        source="medico.nombre_completo", read_only=True
    )
    paciente_nombre = serializers.CharField(
        source="paciente.nombre_completo", read_only=True
    )

    class Meta:
        model = Teleconsulta
        fields = (
            "id", "codigo", "solicitud", "medico", "medico_nombre",
            "paciente", "paciente_nombre", "estado", "fecha_programada",
            "enlace_sala", "motivo", "diagnostico", "notas", "creado_en",
        )
        read_only_fields = (
            "id", "codigo", "estado", "enlace_sala", "diagnostico",
            "notas", "creado_en",
        )


class AgendarTeleconsultaSerializer(serializers.Serializer):
    medico = serializers.IntegerField()
    paciente = serializers.IntegerField()
    fecha_programada = serializers.DateTimeField()
    motivo = serializers.CharField(max_length=200)
    solicitud = serializers.IntegerField(required=False, allow_null=True)


class FinalizarTeleconsultaSerializer(serializers.Serializer):
    diagnostico = serializers.CharField(required=False, allow_blank=True, default="")
    notas = serializers.CharField(required=False, allow_blank=True, default="")


class MedicamentoInputSerializer(serializers.Serializer):
    medicamento = serializers.CharField(max_length=150)
    dosis = serializers.CharField(max_length=80)
    frecuencia = serializers.CharField(max_length=80)
    duracion = serializers.CharField(max_length=80)


class EmitirRecetaSerializer(serializers.Serializer):
    indicaciones_generales = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    medicamentos = MedicamentoInputSerializer(many=True)


class HistorialClinicoSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(
        source="paciente.nombre_completo", read_only=True
    )

    class Meta:
        model = HistorialClinico
        fields = (
            "id", "paciente", "paciente_nombre", "teleconsulta",
            "descripcion", "diagnostico", "creado_en",
        )
        read_only_fields = ("id", "creado_en")
