"""
Paquete de configuracion del proyecto SAMR.

Se importa la instancia de Celery para que quede disponible al iniciar
Django y para que @shared_task funcione en todas las apps.
"""
from .celery import app as celery_app

__all__ = ("celery_app",)
