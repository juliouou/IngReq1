"""Configuracion para el entorno de produccion."""
from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1")  # noqa: F405

# En produccion se recomienda un broker real (Redis). Si CELERY_TASK_ALWAYS_EAGER
# es False, se necesita un worker de Celery en ejecucion.
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", "False")  # noqa: F405

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "")  # noqa: F405

# Endurecimiento basico de seguridad.
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
