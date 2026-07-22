"""Servicios de la app teleconsulta (Service Layer)."""
from django.db import transaction

from core.exceptions import ConflictoEstado, ReglaNegocioError
from core.services import BaseService
from core.utils import generar_codigo
from apps.triaje.models import EstadoSolicitud
from apps.triaje.services import SolicitudService
from apps.teleconsulta.models import (
    DetalleReceta,
    EstadoTeleconsulta,
    HistorialClinico,
    Receta,
    Teleconsulta,
)
from apps.teleconsulta.repositories import RecetaRepository, TeleconsultaRepository


class TeleconsultaService(BaseService):
    repository_class = TeleconsultaRepository

    @transaction.atomic
    def agendar(self, medico, paciente, fecha_programada, motivo, solicitud=None):
        if getattr(medico, "es_medico", False) is False and not medico.is_superuser:
            raise ReglaNegocioError("El usuario indicado no es medico.")
        teleconsulta = self.repository.crear(
            codigo=generar_codigo("TC-", 8),
            solicitud=solicitud,
            medico=medico,
            paciente=paciente,
            fecha_programada=fecha_programada,
            motivo=motivo,
            enlace_sala="https://salas.samr.local/{0}".format(generar_codigo("", 10)),
        )
        return teleconsulta

    @transaction.atomic
    def iniciar(self, teleconsulta):
        if teleconsulta.estado != EstadoTeleconsulta.PROGRAMADA:
            raise ConflictoEstado("Solo se puede iniciar una teleconsulta programada.")
        teleconsulta.estado = EstadoTeleconsulta.EN_CURSO
        teleconsulta.save(update_fields=["estado", "actualizado_en"])
        return teleconsulta

    @transaction.atomic
    def finalizar(self, teleconsulta, diagnostico="", notas=""):
        if teleconsulta.estado == EstadoTeleconsulta.FINALIZADA:
            raise ConflictoEstado("La teleconsulta ya esta finalizada.")

        teleconsulta.estado = EstadoTeleconsulta.FINALIZADA
        teleconsulta.diagnostico = diagnostico
        teleconsulta.notas = notas
        teleconsulta.save(
            update_fields=["estado", "diagnostico", "notas", "actualizado_en"]
        )

        # Cierra la solicitud de origen si existe.
        if teleconsulta.solicitud is not None:
            SolicitudService().cambiar_estado(
                teleconsulta.solicitud, EstadoSolicitud.ATENDIDA
            )

        # Genera la entrada de historial clinico.
        HistorialClinico.objects.create(
            paciente=teleconsulta.paciente,
            teleconsulta=teleconsulta,
            descripcion="Teleconsulta {0}: {1}".format(
                teleconsulta.codigo, teleconsulta.motivo
            ),
            diagnostico=diagnostico,
        )
        return teleconsulta


class RecetaService(BaseService):
    repository_class = RecetaRepository

    @transaction.atomic
    def emitir(self, teleconsulta, indicaciones_generales="", medicamentos=None):
        if not teleconsulta.esta_finalizada:
            raise ReglaNegocioError(
                "Solo se puede emitir una receta de una teleconsulta finalizada."
            )
        if hasattr(teleconsulta, "receta"):
            raise ConflictoEstado("La teleconsulta ya tiene una receta emitida.")

        receta = Receta.objects.create(
            codigo=generar_codigo("REC-", 8),
            teleconsulta=teleconsulta,
            indicaciones_generales=indicaciones_generales,
        )
        for item in (medicamentos or []):
            DetalleReceta.objects.create(
                receta=receta,
                medicamento=item["medicamento"],
                dosis=item["dosis"],
                frecuencia=item["frecuencia"],
                duracion=item["duracion"],
            )
        return receta
