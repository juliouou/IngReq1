"""Repositorios de la app auditoria."""
from core.repositories import BaseRepository
from apps.auditoria.models import RegistroAuditoria


class RegistroAuditoriaRepository(BaseRepository):
    model = RegistroAuditoria

    def listar_por_usuario(self, usuario_id):
        return self.get_queryset().filter(usuario_id=usuario_id)

    def listar_por_accion(self, accion):
        return self.get_queryset().filter(accion=accion)
