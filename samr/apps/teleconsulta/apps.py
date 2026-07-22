"""Configuracion de la app teleconsulta."""
from django.apps import AppConfig


class TeleconsultaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.teleconsulta"
    verbose_name = "Teleconsulta"

    def ready(self):
        from apps.teleconsulta import signals  # noqa: F401
