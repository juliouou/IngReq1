"""Repositorios de la app triaje."""
from core.repositories import BaseRepository
from apps.triaje.models import (
    EstadoSolicitud,
    EvaluacionTriaje,
    SolicitudAtencion,
)


class SolicitudRepository(BaseRepository):
    model = SolicitudAtencion

    def listar_pendientes(self):
        return self.get_queryset().filter(estado=EstadoSolicitud.PENDIENTE)

    def listar_por_paciente(self, paciente_id):
        return self.get_queryset().filter(paciente_id=paciente_id)


class EvaluacionTriajeRepository(BaseRepository):
    model = EvaluacionTriaje

    def listar_criticas(self):
        return self.get_queryset().filter(nivel_urgencia__lte=2)
