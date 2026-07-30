"""Servicios de la app triaje (Service Layer)."""
from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from shared.constants import Roles
from shared.exceptions import ConflictoEstado
from shared.services import BaseService
from shared.utils import generar_codigo
from apps.triaje.models import EstadoSolicitud, EvaluacionTriaje, TipoOrigenSolicitud
from apps.triaje.repositories import SolicitudRepository

# Nota: Usuario, EstadoTeleconsulta, TeleconsultaService y
# RegistroAuditoriaService se siguen importando DENTRO de asignar_medico()
# (no aquí arriba) porque sí forman una dependencia circular real:
# apps.teleconsulta.services importa cosas de apps.triaje. Los demás imports
# que sí eran innecesarios ya se subieron aquí arriba.


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
        # Imports locales: rompen el ciclo apps.triaje <-> apps.teleconsulta
        # (ver nota junto a los imports del encabezado del archivo).
        from apps.usuarios.models import Usuario
        from apps.teleconsulta.models import EstadoTeleconsulta
        from apps.teleconsulta.services import TeleconsultaService
        from apps.auditoria.services import RegistroAuditoriaService

        if not hasattr(solicitud, "evaluacion"):
            return None

        # select_for_update(): bloquea las filas de los medicos candidatos
        # hasta que esta transaccion termine. Sin esto, dos solicitudes de
        # triaje casi simultaneas podian leer el MISMO medico como "el menos
        # cargado" antes de que ninguna terminara de agendarlo -- el mismo
        # tipo de condicion de carrera que resolvimos en Order.accept() de
        # la distribuidora al bloquear StockLevel antes de descontar stock.
        medico_disponible = (
            Usuario.objects.select_for_update()
            .filter(rol=Roles.MEDICO, is_active=True)
            .annotate(
                carga=Count(
                    "teleconsultas_como_medico",
                    filter=Q(
                        teleconsultas_como_medico__estado__in=[
                            EstadoTeleconsulta.PROGRAMADA,
                            EstadoTeleconsulta.EN_CURSO,
                        ]
                    ),
                )
            )
            .order_by("carga")
            .first()
        )

        if not medico_disponible:
            RegistroAuditoriaService().registrar(
                usuario=solicitud.paciente,
                accion="matching_fallido",
                ruta=f"/solicitudes/{solicitud.codigo}",
                codigo_estado=404,
                entidad="SolicitudAtencion",
                entidad_id=solicitud.codigo,
                estado_nuevo={"resultado": "sin_medico_disponible"},
            )
            return None

        nivel = solicitud.evaluacion.nivel_urgencia
        minutos = 2 if nivel in (1, 2) else 15 + (nivel * 5)
        fecha_programada = timezone.now() + timedelta(minutes=minutos)

        teleconsulta = TeleconsultaService().agendar(
            medico=medico_disponible,
            paciente=solicitud.paciente,
            fecha_programada=fecha_programada,
            motivo=f"Evaluación de triaje: {solicitud.motivo}",
            solicitud=solicitud,
        )

        RegistroAuditoriaService().registrar(
            usuario=solicitud.paciente,
            accion="medico_asignado",
            ruta=f"/solicitudes/{solicitud.codigo}",
            codigo_estado=201,
            entidad="SolicitudAtencion",
            entidad_id=solicitud.codigo,
            estado_nuevo={
                "medico_id": medico_disponible.id,
                "teleconsulta_codigo": teleconsulta.codigo,
            },
        )
        return teleconsulta
