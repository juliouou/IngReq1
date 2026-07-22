"""Vistas (ViewSets) de la app triaje."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import EsAdminOMedico
from apps.triaje.models import SolicitudAtencion
from apps.triaje.serializers import (
    RegistrarTriajeSerializer,
    SolicitudAtencionSerializer,
    SolicitudCreateSerializer,
)
from apps.triaje.services import SolicitudService


class SolicitudAtencionViewSet(viewsets.ModelViewSet):
    """Gestion de solicitudes de atencion y su evaluacion de triaje."""

    queryset = (
        SolicitudAtencion.objects
        .select_related("paciente", "evaluacion")
        .all()
    )
    service = SolicitudService()
    filterset_fields = ["estado", "paciente"]
    search_fields = ["codigo", "motivo", "sintomas"]
    ordering_fields = ["creado_en", "estado"]

    def get_serializer_class(self):
        if self.action == "create":
            return SolicitudCreateSerializer
        return SolicitudAtencionSerializer

    def get_permissions(self):
        if self.action == "registrar_triaje":
            return [EsAdminOMedico()]
        return [IsAuthenticated()]

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser or getattr(usuario, "es_admin", False):
            return self.queryset
        if getattr(usuario, "es_medico", False):
            return self.queryset
        # Un paciente solo ve sus propias solicitudes.
        return self.queryset.filter(paciente=usuario)

    def perform_create(self, serializer):
        solicitud = self.service.crear_solicitud(
            paciente=self.request.user,
            motivo=serializer.validated_data["motivo"],
            sintomas=serializer.validated_data["sintomas"],
        )
        serializer.instance = solicitud

    @action(detail=True, methods=["post"], url_path="triaje")
    def registrar_triaje(self, request, pk=None):
        solicitud = self.get_object()
        entrada = RegistrarTriajeSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        evaluacion = self.service.registrar_triaje(
            solicitud=solicitud,
            evaluado_por=request.user,
            **entrada.validated_data,
        )
        salida = SolicitudAtencionSerializer(evaluacion.solicitud)
        return Response(salida.data, status=status.HTTP_201_CREATED)
