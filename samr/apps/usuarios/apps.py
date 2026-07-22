"""Configuracion de la app usuarios."""
from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.usuarios"
    verbose_name = "Usuarios"

    def ready(self):
        # Registra los signals al iniciar la app.
        from apps.usuarios import signals  # noqa: F401
