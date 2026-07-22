"""Vistas (ViewSets) de la app biometria."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.pagination import LargePagination
from core.permissions import EsAdminOMedico
from apps.biometria.models import Alerta, DispositivoIoT, LecturaBiometrica
from apps.biometria.serializers import (
    AlertaSerializer,
    DispositivoIoTSerializer,
    LecturaBiometricaSerializer,
    RegistrarLecturaSerializer,
)
from apps.biometria.services import LecturaService


class DispositivoIoTViewSet(viewsets.ModelViewSet):
    """CRUD de dispositivos IoT."""

    queryset = DispositivoIoT.objects.select_related("paciente").all()
    serializer_class = DispositivoIoTSerializer
    filterset_fields = ["tipo", "activo", "paciente"]
    search_fields = ["codigo", "nombre", "numero_serie"]
    ordering_fields = ["creado_en"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsAdminOMedico()]
        return [IsAuthenticated()]


class LecturaBiometricaViewSet(viewsets.ModelViewSet):
    """Registro y consulta de lecturas biometricas."""

    queryset = LecturaBiometrica.objects.select_related("dispositivo").all()
    serializer_class = LecturaBiometricaSerializer
    pagination_class = LargePagination
    service = LecturaService()
    filterset_fields = ["dispositivo", "tipo_signo", "fuera_de_rango"]
    ordering_fields = ["tomada_en"]

    def get_permissions(self):
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        entrada = RegistrarLecturaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        lectura = self.service.registrar_lectura(
            dispositivo=entrada.validated_data["dispositivo"],
            tipo_signo=entrada.validated_data["tipo_signo"],
            valor=entrada.validated_data["valor"],
            unidad=entrada.validated_data.get("unidad", ""),
        )
        salida = LecturaBiometricaSerializer(lectura)
        return Response(salida.data, status=status.HTTP_201_CREATED)


class AlertaViewSet(viewsets.ModelViewSet):
    """Gestion de alertas biometricas."""

    queryset = Alerta.objects.select_related("paciente", "lectura").all()
    serializer_class = AlertaSerializer
    filterset_fields = ["nivel", "atendida", "paciente"]
    ordering_fields = ["creado_en"]

    def get_permissions(self):
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"], permission_classes=[EsAdminOMedico])
    def atender(self, request, pk=None):
        alerta = self.get_object()
        alerta.atendida = True
        alerta.save(update_fields=["atendida", "actualizado_en"])
        return Response(AlertaSerializer(alerta).data)
