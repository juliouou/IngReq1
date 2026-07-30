"""Configuracion para el entorno de desarrollo local."""
from .base import *  # noqa: F401,F403

DEBUG = True

# Celery sincrono: las tareas se ejecutan en el momento, sin worker ni broker.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

CORS_ALLOW_ALL_ORIGINS = True

# Permite todos los hosts locales durante el desarrollo.
ALLOWED_HOSTS = ["*"]
