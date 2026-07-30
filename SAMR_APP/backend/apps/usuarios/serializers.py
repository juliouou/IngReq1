"""Serializers de la app usuarios."""
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from shared.validators import validar_cedula_ecuatoriana
from apps.usuarios.models import PerfilMedico, PerfilPaciente, Usuario


def _validar_cedula_opcional(value):
    if value:
        try:
            validar_cedula_ecuatoriana(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
    return value


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Usuario
        fields = (
            "id", "email", "nombres", "apellidos", "nombre_completo",
            "cedula", "telefono", "rol", "is_active", "creado_en",
        )
        read_only_fields = ("id", "creado_en", "is_active")


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = (
            "id", "email", "nombres", "apellidos",
            "cedula", "telefono", "rol", "password",
        )

    def validate_cedula(self, value):
        return _validar_cedula_opcional(value)


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ("nombres", "apellidos", "cedula", "telefono", "rol", "is_active")

    def validate_cedula(self, value):
        return _validar_cedula_opcional(value)


class PerfilMedicoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source="usuario", write_only=True
    )

    class Meta:
        model = PerfilMedico
        fields = (
            "id", "usuario", "usuario_id", "especialidad", "numero_registro",
            "anios_experiencia", "disponible", "creado_en",
        )
        read_only_fields = ("id", "creado_en")


class PerfilPacienteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source="usuario", write_only=True
    )

    class Meta:
        model = PerfilPaciente
        fields = (
            "id", "usuario", "usuario_id", "fecha_nacimiento", "tipo_sangre",
            "alergias", "antecedentes", "creado_en",
        )
        read_only_fields = ("id", "creado_en")
