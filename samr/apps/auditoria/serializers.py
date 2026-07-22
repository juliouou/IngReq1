"""Serializers de la app auditoria."""
from rest_framework import serializers

from apps.auditoria.models import RegistroAuditoria


class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    usuario_email = serializers.EmailField(
        source="usuario.email", read_only=True, default=None
    )

    class Meta:
        model = RegistroAuditoria
        fields = (
            "id", "usuario", "usuario_email", "accion", "ruta",
            "codigo_estado", "request_id", "ip", "creado_en",
        )
        read_only_fields = fields
