"""Permisos base por rol (autorizacion) reutilizables por las apps."""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from shared.constants import Roles


class RolePermission(BasePermission):
    """Permite el acceso solo a los roles declarados en `roles_permitidos`."""

    roles_permitidos = ()
    message = "No tiene el rol requerido para esta accion."

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            return False
        if usuario.is_superuser:
            return True
        return getattr(usuario, "rol", None) in self.roles_permitidos


class EsAdmin(RolePermission):
    roles_permitidos = (Roles.ADMIN,)


class EsMedico(RolePermission):
    roles_permitidos = (Roles.MEDICO,)


class EsPaciente(RolePermission):
    roles_permitidos = (Roles.PACIENTE,)


class EsAdminOMedico(RolePermission):
    roles_permitidos = (Roles.ADMIN, Roles.MEDICO)


class EsAdminOSoloLectura(BasePermission):
    """Lectura para cualquier autenticado; escritura solo para admin."""

    message = "Solo un administrador puede modificar este recurso."

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return usuario.is_superuser or getattr(usuario, "rol", None) == Roles.ADMIN
