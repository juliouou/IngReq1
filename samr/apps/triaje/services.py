"""Servicios de la app triaje (Service Layer)."""
from django.db import transaction

from core.exceptions import ConflictoEstado
from core.services import BaseService
from core.utils import generar_codigo
from apps.triaje.models import EstadoSolicitud, EvaluacionTriaje
from apps.triaje.repositories import SolicitudRepository


class SolicitudService(BaseService):
    repository_class = SolicitudRepository

    @transaction.atomic
    def crear_solicitud(self, paciente, motivo, sintomas):
        return self.repository.crear(
            codigo=generar_codigo("SOL-", 8),
            paciente=paciente,
            motivo=motivo,
            sintomas=sintomas,
            estado=EstadoSolicitud.PENDIENTE,
        )

    @transaction.atomic
    def registrar_triaje(self, solicitud, evaluado_por=None, **datos):
        if solicitud.esta_cerrada:
            raise ConflictoEstado(
                "No se puede evaluar una solicitud ya cerrada."
            )
        evaluacion, _creada = EvaluacionTriaje.objects.update_or_create(
            solicitud=solicitud,
            defaults={"evaluado_por": evaluado_por, **datos},
        )
        solicitud.estado = EstadoSolicitud.EN_TRIAJE
        solicitud.save(update_fields=["estado", "actualizado_en"])
        return evaluacion

    @transaction.atomic
    def cambiar_estado(self, solicitud, nuevo_estado):
        validos = dict(EstadoSolicitud.CHOICES)
        if nuevo_estado not in validos:
            raise ConflictoEstado("Estado de solicitud no valido.")
        solicitud.estado = nuevo_estado
        solicitud.save(update_fields=["estado", "actualizado_en"])
        return solicitud
