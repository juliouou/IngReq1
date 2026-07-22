"""Vistas (ViewSets) de la app usuarios."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import EsAdmin, EsAdminOMedico
from apps.usuarios.models import PerfilMedico, PerfilPaciente, Usuario
from apps.usuarios.serializers import (
    PerfilMedicoSerializer,
    PerfilPacienteSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
    UsuarioUpdateSerializer,
)
from apps.usuarios.services import UsuarioService


class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios. Escritura restringida a administradores."""

    queryset = Usuario.objects.all()
    service = UsuarioService()
    filterset_fields = ["rol", "is_active"]
    search_fields = ["email", "nombres", "apellidos", "cedula"]
    ordering_fields = ["creado_en", "email"]

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCreateSerializer
        if self.action in ("update", "partial_update"):
            return UsuarioUpdateSerializer
        return UsuarioSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        datos = dict(serializer.validated_data)
        password = datos.pop("password", None)
        usuario = self.service.registrar(password=password, **datos)
        serializer.instance = usuario

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


class PerfilMedicoViewSet(viewsets.ModelViewSet):
    """CRUD de perfiles de medico."""

    queryset = PerfilMedico.objects.select_related("usuario").all()
    serializer_class = PerfilMedicoSerializer
    filterset_fields = ["especialidad", "disponible"]
    search_fields = [
        "especialidad", "numero_registro",
        "usuario__nombres", "usuario__apellidos",
    ]
    ordering_fields = ["creado_en", "anios_experiencia"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsAdminOMedico()]
        return [IsAuthenticated()]


class PerfilPacienteViewSet(viewsets.ModelViewSet):
    """CRUD de perfiles de paciente."""

    queryset = PerfilPaciente.objects.select_related("usuario").all()
    serializer_class = PerfilPacienteSerializer
    filterset_fields = ["tipo_sangre"]
    search_fields = ["usuario__nombres", "usuario__apellidos", "usuario__cedula"]
    ordering_fields = ["creado_en"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [EsAdminOMedico()]
        return [IsAuthenticated()]
