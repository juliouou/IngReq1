"""Configuracion de la app biometria."""
from django.apps import AppConfig


class BiometriaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.biometria"
    verbose_name = "Biometria"

    def ready(self):
        from apps.biometria import signals  # noqa: F401
