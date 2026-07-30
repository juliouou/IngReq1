"""Repositorios de la app teleconsulta."""
from shared.repositories import BaseRepository
from apps.teleconsulta.models import (
    HistorialClinico,
    Receta,
    Teleconsulta,
)


class TeleconsultaRepository(BaseRepository):
    model = Teleconsulta

    def listar_por_medico(self, medico_id):
        return self.get_queryset().filter(medico_id=medico_id)

    def listar_por_paciente(self, paciente_id):
        return self.get_queryset().filter(paciente_id=paciente_id)


class RecetaRepository(BaseRepository):
    model = Receta


class HistorialClinicoRepository(BaseRepository):
    model = HistorialClinico

    def listar_por_paciente(self, paciente_id):
        return self.get_queryset().filter(paciente_id=paciente_id)
