import uuid
from datetime import datetime, timezone

from app import db


class CapturaBiometrica(db.Model):
    """RF-09: Captura Continua de Flujos Biométricos IoT.
    Nombre de clase alineado con SAMR_SRS (no usar 'FlujoBiometrico')."""

    __tablename__ = "capturas_biometricas"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paciente_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    ekg = db.Column(db.Float, nullable=True)
    eeg = db.Column(db.Float, nullable=True)
    spo2 = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # TODO Antonella (RF-10): invocar MedGeminiEngine.detectarAnomalia(lecturas)


class AlertaPredictivaXAI(db.Model):
    """RF-10/RF-11: alerta generada por MedGeminiEngine a partir de una
    CapturaBiometrica. Nombre de clase alineado con SAMR_SRS
    (no usar 'AlertaBiometrica')."""

    __tablename__ = "alertas_predictivas_xai"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    captura_id = db.Column(db.String(36), db.ForeignKey("capturas_biometricas.id"), nullable=False)
    nivel_riesgo = db.Column(db.String(20), nullable=False)
    explicacion_xai = db.Column(db.Text, nullable=True)
    atendida = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # TODO Antonella (RF-11, RF-12): notificar a BotConversacional y CentroAsistencia
