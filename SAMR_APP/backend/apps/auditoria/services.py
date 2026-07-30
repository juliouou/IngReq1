"""Servicios de la app auditoria (Service Layer)."""
from shared.services import BaseService
from apps.auditoria.repositories import RegistroAuditoriaRepository


class RegistroAuditoriaService(BaseService):
    repository_class = RegistroAuditoriaRepository

    def registrar(
        self,
        usuario,
        accion,
        ruta="",
        codigo_estado=None,
        request_id="",
        ip=None,
        entidad="",
        entidad_id="",
        estado_anterior=None,
        estado_nuevo=None,
    ):
        """
        Crea un registro de auditoria.

        Sigue aceptando las llamadas existentes (usuario, accion, ruta,
        codigo_estado) sin cambios. Los parametros nuevos (entidad,
        entidad_id, estado_anterior, estado_nuevo) son opcionales: usalos
        cuando quieras registrar el cambio de negocio real, no solo el
        metodo/ruta HTTP -- ver SolicitudService.asignar_medico() para un
        ejemplo.
        """
        return self.repository.crear(
            usuario=usuario,
            accion=accion,
            ruta=(ruta or "")[:255],
            codigo_estado=codigo_estado,
            request_id=request_id,
            ip=ip,
            entidad=entidad,
            entidad_id=str(entidad_id) if entidad_id else "",
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
        )
