"""Serializers de la app triaje."""
from rest_framework import serializers

from apps.triaje.models import EvaluacionTriaje, SolicitudAtencion


class EvaluacionTriajeSerializer(serializers.ModelSerializer):
    es_critica = serializers.BooleanField(read_only=True)

    class Meta:
        model = EvaluacionTriaje
        fields = (
            "id", "solicitud", "evaluado_por", "nivel_urgencia",
            "observaciones", "temperatura", "frecuencia_cardiaca",
            "es_critica", "creado_en",
        )
        read_only_fields = ("id", "creado_en", "evaluado_por", "solicitud")


class SolicitudAtencionSerializer(serializers.ModelSerializer):
    evaluacion = EvaluacionTriajeSerializer(read_only=True)
    paciente_nombre = serializers.CharField(
        source="paciente.nombre_completo", read_only=True
    )

    class Meta:
        model = SolicitudAtencion
        fields = (
            "id", "codigo", "paciente", "paciente_nombre", "motivo",
            "sintomas", "estado", "evaluacion", "creado_en",
        )
        read_only_fields = ("id", "codigo", "estado", "creado_en", "paciente")


class SolicitudCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudAtencion
        fields = ("motivo", "sintomas")


class RegistrarTriajeSerializer(serializers.Serializer):
    nivel_urgencia = serializers.IntegerField(min_value=1, max_value=5)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    temperatura = serializers.DecimalField(
        max_digits=4, decimal_places=1, required=False, allow_null=True
    )
    frecuencia_cardiaca = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )
