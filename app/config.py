import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Configuración base. Cada dev puede sobreescribir con variables de entorno (.env)."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "cambiar-esto-en-produccion")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'samr.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # RF-03: expiración del código MFA (minutos)
    MFA_CODE_EXPIRATION_MINUTES = 5

    # RF-03: expiración del token OAuth (horas)
    JWT_EXPIRATION_HOURS = 8

    # RNF-01 Seguridad: intentos máximos antes de bloquear
    MAX_INTENTOS_MFA = 3
