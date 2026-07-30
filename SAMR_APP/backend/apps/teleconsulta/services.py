"""Servicios de la app teleconsulta (Service Layer)."""
from django.db import transaction

from shared.exceptions import ConflictoEstado, ReglaNegocioError
from shared.services import BaseService
from shared.utils import generar_codigo
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
    def rechazar_y_reasignar(self, teleconsulta, medico_que_rechaza, motivo):
        from django.utils import timezone
        from datetime import timedelta
        from django.contrib.auth import get_user_model
        from shared.constants import Roles
        User = get_user_model()

        if teleconsulta.estado != EstadoTeleconsulta.PROGRAMADA:
            raise ConflictoEstado("Solo se puede rechazar una teleconsulta programada.")
        if not motivo or not str(motivo).strip():
            raise ReglaNegocioError("El motivo de rechazo no puede estar vacío.")

        teleconsulta.estado = EstadoTeleconsulta.CANCELADA
        nombre_medico = medico_que_rechaza.nombre_completo or medico_que_rechaza.email
        teleconsulta.notas = f"Rechazada por Dr(a). {nombre_medico}: {motivo}"
        teleconsulta.save(update_fields=["estado", "notas", "actualizado_en"])

        nuevo_medico = User.objects.filter(rol=Roles.MEDICO).exclude(id=medico_que_rechaza.id).first()
        if not nuevo_medico:
            raise ReglaNegocioError("No hay otro médico disponible para reasignar la teleconsulta.")

        nueva_tc = self.repository.crear(
            codigo=generar_codigo("TC-", 8),
            solicitud=teleconsulta.solicitud,
            medico=nuevo_medico,
            paciente=teleconsulta.paciente,
            fecha_programada=timezone.now() + timedelta(minutes=5),
            motivo=teleconsulta.motivo,
            enlace_sala="https://salas.samr.local/{0}".format(generar_codigo("", 10)),
        )
        return nueva_tc

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

        # Obtener signos vitales recientes del paciente si existen
        from apps.biometria.models import LecturaBiometrica
        lecturas_recientes = LecturaBiometrica.objects.filter(
            dispositivo__paciente=teleconsulta.paciente
        ).order_by("-tomada_en")[:5]

        signos_vitales_fhir = []
        for l in lecturas_recientes:
            signos_vitales_fhir.append({
                "tipo": l.get_tipo_signo_display(),
                "valor": str(l.valor),
                "unidad": l.unidad,
                "fecha": l.tomada_en.isoformat() if l.tomada_en else ""
            })

        medicamentos_fhir = []
        if hasattr(teleconsulta, "receta") and teleconsulta.receta:
            for d in teleconsulta.receta.detalles.all():
                medicamentos_fhir.append({
                    "nombre": d.medicamento,
                    "dosis": d.dosis,
                    "frecuencia": d.frecuencia,
                    "duracion": d.duracion,
                })

        contenido_fhir = {
            "resourceType": "Encounter",
            "status": "finished",
            "periodo": {
                "inicio": teleconsulta.creado_en.isoformat() if teleconsulta.creado_en else "",
                "fin": teleconsulta.actualizado_en.isoformat() if teleconsulta.actualizado_en else "",
            },
            "paciente": {
                "id": str(teleconsulta.paciente.id),
                "nombre": teleconsulta.paciente.nombre_completo,
            },
            "medico": {
                "id": str(teleconsulta.medico.id),
                "nombre": teleconsulta.medico.nombre_completo,
            },
            "diagnostico": [{
                "texto": diagnostico,
                "sistema_clasificacion": "CIE-10",
                "codigo": None
            }],
            "medicamentos": medicamentos_fhir,
            "signos_vitales": signos_vitales_fhir,
            "notas": notas,
        }

        # Genera la entrada de historial clinico.
        HistorialClinico.objects.create(
            paciente=teleconsulta.paciente,
            teleconsulta=teleconsulta,
            descripcion="Teleconsulta {0}: {1}".format(
                teleconsulta.codigo, teleconsulta.motivo
            ),
            diagnostico=diagnostico,
            contenido_fhir=contenido_fhir,
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
        medicamentos_fhir = []
        for item in (medicamentos or []):
            DetalleReceta.objects.create(
                receta=receta,
                medicamento=item["medicamento"],
                dosis=item["dosis"],
                frecuencia=item["frecuencia"],
                duracion=item["duracion"],
            )
            medicamentos_fhir.append({
                "nombre": item["medicamento"],
                "dosis": item["dosis"],
                "frecuencia": item["frecuencia"],
                "duracion": item["duracion"],
            })

        # Actualiza el documento FHIR en el HistorialClinico correspondiente
        historial = HistorialClinico.objects.filter(teleconsulta=teleconsulta).first()
        if historial:
            if not historial.contenido_fhir:
                historial.contenido_fhir = {}
            historial.contenido_fhir["medicamentos"] = medicamentos_fhir
            historial.save(update_fields=["contenido_fhir", "actualizado_en"])

        return receta


class HistorialClinicoService:
    """Servicio para consultas y operaciones sobre el Historial Clinico FHIR."""

    def buscar_por_medicamento(self, nombre_medicamento):
        """
        Busca entradas de historial clinico que contengan un medicamento especifico
        en su documento FHIR utilizando el operador de contencion JSONB (@>).
        """
        return HistorialClinico.objects.filter(
            contenido_fhir__medicamentos__contains=[{"nombre": nombre_medicamento}]
        )

