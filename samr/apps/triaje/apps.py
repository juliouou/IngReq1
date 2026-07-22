"""Configuracion de la app triaje."""
from django.apps import AppConfig


class TriajeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.triaje"
    verbose_name = "Triaje"

    def ready(self):
        from apps.triaje import signals  # noqa: F401
