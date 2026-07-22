"""Repositorios de la app usuarios (Repository Pattern)."""
from core.constants import Roles
from core.repositories import BaseRepository
from apps.usuarios.models import PerfilMedico, PerfilPaciente, Usuario


class UsuarioRepository(BaseRepository):
    model = Usuario

    def obtener_por_email(self, email):
        return self.get_queryset().filter(email=email).first()

    def listar_por_rol(self, rol):
        return self.get_queryset().filter(rol=rol)

    def listar_medicos(self):
        return self.get_queryset().filter(rol=Roles.MEDICO)

    def listar_pacientes(self):
        return self.get_queryset().filter(rol=Roles.PACIENTE)


class PerfilMedicoRepository(BaseRepository):
    model = PerfilMedico

    def listar_disponibles(self):
        return self.get_queryset().filter(disponible=True)


class PerfilPacienteRepository(BaseRepository):
    model = PerfilPaciente
