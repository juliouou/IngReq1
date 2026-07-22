"""Serializers de la app biometria."""
from rest_framework import serializers

from apps.biometria.models import Alerta, DispositivoIoT, LecturaBiometrica


class DispositivoIoTSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(
        source="paciente.nombre_completo", read_only=True
    )

    class Meta:
        model = DispositivoIoT
        fields = (
            "id", "codigo", "nombre", "tipo", "paciente", "paciente_nombre",
            "numero_serie", "activo", "creado_en",
        )
        read_only_fields = ("id", "codigo", "creado_en")


class LecturaBiometricaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturaBiometrica
        fields = (
            "id", "dispositivo", "tipo_signo", "valor", "unidad",
            "fuera_de_rango", "tomada_en",
        )
        read_only_fields = ("id", "fuera_de_rango", "tomada_en")


class RegistrarLecturaSerializer(serializers.Serializer):
    dispositivo = serializers.PrimaryKeyRelatedField(
        queryset=DispositivoIoT.objects.all()
    )
    tipo_signo = serializers.CharField()
    valor = serializers.DecimalField(max_digits=6, decimal_places=2)
    unidad = serializers.CharField(required=False, allow_blank=True, default="")


class AlertaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(
        source="paciente.nombre_completo", read_only=True
    )

    class Meta:
        model = Alerta
        fields = (
            "id", "lectura", "paciente", "paciente_nombre", "nivel",
            "mensaje", "atendida", "creado_en",
        )
        read_only_fields = ("id", "creado_en")
