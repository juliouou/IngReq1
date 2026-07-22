"""Servicios de la app auditoria (Service Layer)."""
from core.services import BaseService
from apps.auditoria.repositories import RegistroAuditoriaRepository


class RegistroAuditoriaService(BaseService):
    repository_class = RegistroAuditoriaRepository

    def registrar(self, usuario, accion, ruta, codigo_estado, request_id="", ip=None):
        """Crea un registro de auditoria de forma explicita (uso programatico)."""
        return self.repository.crear(
            usuario=usuario,
            accion=accion,
            ruta=ruta[:255],
            codigo_estado=codigo_estado,
            request_id=request_id,
            ip=ip,
        )
