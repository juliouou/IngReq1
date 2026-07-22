"""Vistas de la app auditoria (solo lectura, exclusivo de administradores)."""
from rest_framework import viewsets

from core.permissions import EsAdmin
from apps.auditoria.models import RegistroAuditoria
from apps.auditoria.serializers import RegistroAuditoriaSerializer


class RegistroAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta de los registros de auditoria. Solo administradores."""

    queryset = RegistroAuditoria.objects.select_related("usuario").all()
    serializer_class = RegistroAuditoriaSerializer
    permission_classes = [EsAdmin]
    filterset_fields = ["accion", "codigo_estado", "usuario"]
    search_fields = ["ruta", "request_id"]
    ordering_fields = ["creado_en", "codigo_estado"]
