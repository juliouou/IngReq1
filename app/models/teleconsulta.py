import uuid
from datetime import datetime, timezone

from app import db


class Teleconsulta(db.Model):
    """RF-13: Teleconsulta con Historial Clínico y Soporte de Med-Gemini."""

    __tablename__ = "teleconsultas"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medico_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    paciente_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    diagnostico = db.Column(db.Text, nullable=True)
    version_med_gemini = db.Column(db.String(20), nullable=True)
    estado = db.Column(
        db.Enum("iniciada", "en_curso", "finalizada", "derivada", name="estado_teleconsulta"),
        default="iniciada",
    )
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # TODO Antonella (RF-13, RF-14): historial clínico + sugerencia diagnóstica Med-Gemini
    # TODO Antonella (RF-15, RF-16): derivación de emergencia y reasignación


class RecetaDigital(db.Model):
    """RF-14: Emisión de Recetas Digitales con Firma Electrónica."""

    __tablename__ = "recetas_digitales"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    teleconsulta_id = db.Column(db.String(36), db.ForeignKey("teleconsultas.id"), nullable=False)
    medicamento = db.Column(db.String(120), nullable=False)
    dosis = db.Column(db.String(80), nullable=False)
    firma_electronica = db.Column(db.String(200), nullable=True)  # TODO Alisson: firma real
    emitida_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
