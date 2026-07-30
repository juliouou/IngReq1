"""Configuracion base compartida por todos los entornos del proyecto SAMR."""
import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Rutas y variables de entorno
# ---------------------------------------------------------------------------

# base.py esta en samr/config/settings/base.py -> subir 3 niveles = samr/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(nombre, por_defecto="False"):
    """Lee una variable de entorno booleana."""
    return os.environ.get(nombre, por_defecto).lower() in ("1", "true", "yes", "on")


def env_list(nombre, por_defecto=""):
    """Lee una variable de entorno como lista separada por comas."""
    crudo = os.environ.get(nombre, por_defecto)
    return [item.strip() for item in crudo.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Seguridad basica
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-clave-por-defecto-cambiar-en-produccion"
)
DEBUG = env_bool("DEBUG", "True")
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")


# ---------------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "channels",
]

LOCAL_APPS = [
    "apps.usuarios",
    "apps.triaje",
    "apps.biometria",
    "apps.teleconsulta",
    "apps.auditoria",
    "apps.portal",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ---------------------------------------------------------------------------
# Middleware (incluye middleware propio de core)
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "shared.middleware.RequestIDMiddleware",
    "shared.middleware.AuditoriaMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.teleconsulta.context_processors.notificaciones_teleconsulta",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ---------------------------------------------------------------------------
# Base de datos (PostgreSQL con fallback a SQLite si no hay DATABASE_URL)
# ---------------------------------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}


# ---------------------------------------------------------------------------
# Channels (capa en memoria: no requiere Redis en desarrollo)
# ---------------------------------------------------------------------------

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


# ---------------------------------------------------------------------------
# Autenticacion y usuario personalizado
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "usuarios.Usuario"

LOGIN_URL = "portal:login"
LOGIN_REDIRECT_URL = "portal:dashboard"
LOGOUT_REDIRECT_URL = "portal:login"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "shared.pagination.DefaultPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "shared.exceptions.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}


# ---------------------------------------------------------------------------
# JWT (Simple JWT)
# ---------------------------------------------------------------------------

JWT_ACCESS_MINUTES = int(os.environ.get("JWT_ACCESS_MINUTES", "60"))
JWT_REFRESH_DAYS = int(os.environ.get("JWT_REFRESH_DAYS", "7"))

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=JWT_ACCESS_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=JWT_REFRESH_DAYS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
}


# ---------------------------------------------------------------------------
# drf-spectacular (Swagger / OpenAPI)
# ---------------------------------------------------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "SAMR API",
    "DESCRIPTION": "Sistema de Atencion Medica Remota - API REST.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
    },
}


# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "memory://")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "cache+memory://")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = os.environ.get("TIME_ZONE", "America/Guayaquil")
# En base se ejecuta de forma sincrona; development lo confirma y production
# puede desactivarlo apuntando a un broker real (ej. Redis).
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", "True")


# ---------------------------------------------------------------------------
# Internacionalizacion
# ---------------------------------------------------------------------------

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "es-ec")
TIME_ZONE = os.environ.get("TIME_ZONE", "America/Guayaquil")
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Archivos estaticos y media
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "samr": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
