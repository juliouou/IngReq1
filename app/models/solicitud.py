import uuid
from datetime import datetime, timezone

from app import db


class Solicitud(db.Model):
    """RF-04 a RF-08: fusiona SolicitudSintomas/AlertaEmergenciaIoT con el
    atributo `tipo_origen` (regla 8 del proyecto: sin subtipos separados)."""

    __tablename__ = "solicitudes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paciente_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    tipo_origen = db.Column(
        db.Enum("bot", "formulario", "iot", name="tipo_origen_solicitud"), nullable=False
    )
    sintomas = db.Column(db.Text, nullable=True)
    nivel_riesgo = db.Column(db.String(20), nullable=True)  # TODO Antonella: definir escala (RF-05)
    explicacion_xai = db.Column(db.Text, nullable=True)
    estado = db.Column(
        db.Enum("pendiente", "clasificada", "asignada", "atendida", name="estado_solicitud"),
        default="pendiente",
    )
    medico_asignado_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=True)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # TODO Antonella (RF-05, RF-08): invocar MedGeminiEngine.clasificar() y MotorMatching.asignar()
