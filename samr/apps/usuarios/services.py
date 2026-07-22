"""Servicios de la app usuarios (Service Layer)."""
from django.db import transaction

from core.exceptions import ReglaNegocioError
from core.services import BaseService
from apps.usuarios.models import Usuario
from apps.usuarios.repositories import UsuarioRepository


class UsuarioService(BaseService):
    repository_class = UsuarioRepository

    @transaction.atomic
    def registrar(self, password=None, **datos):
        email = datos.get("email")
        if email and self.repository.existe(email=email):
            raise ReglaNegocioError("Ya existe un usuario con ese correo.")
        usuario = Usuario.objects.create_user(password=password, **datos)
        return usuario

    @transaction.atomic
    def cambiar_disponibilidad(self, usuario, disponible):
        perfil = getattr(usuario, "perfil_medico", None)
        if perfil is None:
            raise ReglaNegocioError("El usuario no tiene perfil de medico.")
        perfil.disponible = disponible
        perfil.save(update_fields=["disponible", "actualizado_en"])
        return perfil
