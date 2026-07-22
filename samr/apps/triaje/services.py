"""Servicios de la app triaje (Service Layer)."""
from django.db import transaction

from core.exceptions import ConflictoEstado
from core.services import BaseService
from core.utils import generar_codigo
from apps.triaje.models import EstadoSolicitud, EvaluacionTriaje, TipoOrigenSolicitud
from apps.triaje.repositories import SolicitudRepository


class SolicitudService(BaseService):
    repository_class = SolicitudRepository

    @transaction.atomic
    def crear_solicitud(self, paciente, motivo, sintomas, tipo_origen=TipoOrigenSolicitud.CHAT_IA):
        return self.repository.crear(
            codigo=generar_codigo("SOL-", 8),
            paciente=paciente,
            motivo=motivo,
            sintomas=sintomas,
            estado=EstadoSolicitud.PENDIENTE,
            tipo_origen=tipo_origen,
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

    @transaction.atomic
    def asignar_medico(self, solicitud):
        from apps.usuarios.models import Usuario
        from apps.teleconsulta.models import EstadoTeleconsulta
        from apps.teleconsulta.services import TeleconsultaService
        from apps.auditoria.services import RegistroAuditoriaService
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Q
        from core.constants import Roles
        
        if not hasattr(solicitud, "evaluacion"):
            return None
            
        medico_disponible = (
            Usuario.objects.filter(rol=Roles.MEDICO, is_active=True)
            .annotate(
                carga=Count(
                    'teleconsultas_como_medico',
                    filter=Q(teleconsultas_como_medico__estado__in=[
                        EstadoTeleconsulta.PROGRAMADA,
                        EstadoTeleconsulta.EN_CURSO
                    ])
                )
            )
            .order_by('carga')
            .first()
        )
        
        if not medico_disponible:
            RegistroAuditoriaService().registrar(
                usuario=solicitud.paciente,
                accion="matching_fallido",
                ruta=f"/solicitudes/{solicitud.codigo}",
                codigo_estado=404,
                observacion="No hay medicos disponibles para asignar"
            )
            return None
            
        nivel = solicitud.evaluacion.nivel_urgencia
        if nivel in [1, 2]:
            minutos = 2
        else:
            minutos = 15 + (nivel * 5)
            
        fecha_programada = timezone.now() + timedelta(minutes=minutos)
        
        teleconsulta = TeleconsultaService().agendar(
            medico=medico_disponible,
            paciente=solicitud.paciente,
            fecha_programada=fecha_programada,
            motivo=f"Evaluación de triaje: {solicitud.motivo}",
            solicitud=solicitud
        )
        return teleconsulta
