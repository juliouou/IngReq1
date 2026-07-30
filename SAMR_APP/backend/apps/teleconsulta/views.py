"""Vistas (ViewSets) de la app teleconsulta."""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shared.exceptions import RecursoNoEncontrado
from shared.permissions import EsAdminOMedico
from apps.usuarios.models import Usuario
from apps.triaje.models import SolicitudAtencion
from apps.teleconsulta.models import HistorialClinico, Teleconsulta
from apps.teleconsulta.serializers import (
    AgendarTeleconsultaSerializer,
    EmitirRecetaSerializer,
    FinalizarTeleconsultaSerializer,
    HistorialClinicoSerializer,
    RecetaSerializer,
    TeleconsultaSerializer,
)
from apps.teleconsulta.services import RecetaService, TeleconsultaService


class TeleconsultaViewSet(viewsets.ModelViewSet):
    """Gestion del ciclo de vida de una teleconsulta."""

    queryset = Teleconsulta.objects.select_related(
        "medico", "paciente", "solicitud"
    ).all()
    serializer_class = TeleconsultaSerializer
    service = TeleconsultaService()
    receta_service = RecetaService()
    filterset_fields = ["estado", "medico", "paciente"]
    search_fields = ["codigo", "motivo"]
    ordering_fields = ["fecha_programada", "creado_en"]

    def get_permissions(self):
        if self.action in (
            "create", "agendar", "iniciar", "finalizar",
            "emitir_receta", "update", "partial_update", "destroy",
        ):
            return [EsAdminOMedico()]
        return [IsAuthenticated()]

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser or getattr(usuario, "es_admin", False):
            return self.queryset
        if getattr(usuario, "es_medico", False):
            return self.queryset.filter(medico=usuario)
        return self.queryset.filter(paciente=usuario)

    def create(self, request, *args, **kwargs):
        return self._agendar(request)

    @action(detail=False, methods=["post"])
    def agendar(self, request):
        return self._agendar(request)

    def _agendar(self, request):
        entrada = AgendarTeleconsultaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        medico = Usuario.objects.filter(pk=datos["medico"]).first()
        paciente = Usuario.objects.filter(pk=datos["paciente"]).first()
        if medico is None or paciente is None:
            raise RecursoNoEncontrado("Medico o paciente inexistente.")

        solicitud = None
        if datos.get("solicitud"):
            solicitud = SolicitudAtencion.objects.filter(
                pk=datos["solicitud"]
            ).first()

        teleconsulta = self.service.agendar(
            medico=medico,
            paciente=paciente,
            fecha_programada=datos["fecha_programada"],
            motivo=datos["motivo"],
            solicitud=solicitud,
        )
        salida = TeleconsultaSerializer(teleconsulta)
        return Response(salida.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def iniciar(self, request, pk=None):
        teleconsulta = self.get_object()
        self.service.iniciar(teleconsulta)
        return Response(TeleconsultaSerializer(teleconsulta).data)

    @action(detail=True, methods=["post"])
    def finalizar(self, request, pk=None):
        teleconsulta = self.get_object()
        entrada = FinalizarTeleconsultaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        self.service.finalizar(
            teleconsulta,
            diagnostico=entrada.validated_data["diagnostico"],
            notas=entrada.validated_data["notas"],
        )
        return Response(TeleconsultaSerializer(teleconsulta).data)

    @action(detail=True, methods=["post"], url_path="receta")
    def emitir_receta(self, request, pk=None):
        teleconsulta = self.get_object()
        entrada = EmitirRecetaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        receta = self.receta_service.emitir(
            teleconsulta=teleconsulta,
            indicaciones_generales=entrada.validated_data["indicaciones_generales"],
            medicamentos=entrada.validated_data["medicamentos"],
        )
        return Response(RecetaSerializer(receta).data, status=status.HTTP_201_CREATED)


class HistorialClinicoViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta del historial clinico (solo lectura por API)."""

    queryset = HistorialClinico.objects.select_related(
        "paciente", "teleconsulta"
    ).all()
    serializer_class = HistorialClinicoSerializer
    filterset_fields = ["paciente"]
    ordering_fields = ["creado_en"]

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser or getattr(usuario, "es_admin", False):
            return self.queryset
        if getattr(usuario, "es_medico", False):
            return self.queryset
        return self.queryset.filter(paciente=usuario)
