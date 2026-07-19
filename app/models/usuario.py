import uuid
from datetime import datetime, timezone

from app import db


class Usuario(db.Model):
    """RF-01: Registro y Gestión de Perfiles con Roles.
    Fusiona Paciente/Medico/Administrativo con el atributo `rol` (según
    el diagrama de clases unificado, regla 8 del proyecto)."""

    __tablename__ = "usuarios"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cedula = db.Column(db.String(10), unique=True, nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    afiliacion_iess = db.Column(db.String(50), nullable=True)  # RF-02
    dispositivo_iot_id = db.Column(db.String(50), nullable=True)  # RF-09
    rol = db.Column(
        db.Enum("paciente", "medico", "administrativo", name="rol_usuario"),
        nullable=False,
        default="paciente",
    )
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    consentimiento = db.relationship(
        "ConsentimientoLOPDP", backref="usuario", uselist=False
    )

    def __repr__(self):
        return f"<Usuario {self.cedula} rol={self.rol}>"


class CodigoMFA(db.Model):
    """RF-03: código de un solo uso para autenticación multifactor.
    Representa la parte 'ServicioMFA' que en los diagramas de secuencia
    se pliega como llamada reflexiva de FormularioRegistro/Sesion."""

    __tablename__ = "codigos_mfa"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    codigo = db.Column(db.String(6), nullable=False)
    expira_en = db.Column(db.DateTime, nullable=False)
    intentos = db.Column(db.Integer, default=0)
    usado = db.Column(db.Boolean, default=False)


class ConsentimientoLOPDP(db.Model):
    """RF-18: Registro de Consentimiento Explícito LOPDP."""

    __tablename__ = "consentimientos_lopdp"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    activo = db.Column(db.Boolean, default=False)
    version_politica = db.Column(db.String(10), default="1.0")
    aceptado_en = db.Column(db.DateTime, nullable=True)
