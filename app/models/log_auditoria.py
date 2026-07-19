import hashlib
import uuid
from datetime import datetime, timezone

from app import db


class LogAuditoria(db.Model):
    """RF-20: Logs de Auditoría Inmutables con Hash Criptográfico.
    Cualquier módulo puede escribir aquí vía LogAuditoria.registrar(...)."""

    __tablename__ = "logs_auditoria"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = db.Column(db.String(36), nullable=True)
    tipo_evento = db.Column(db.String(80), nullable=False)
    modulo = db.Column(db.String(10), nullable=False)  # M1..M5
    version_med_gemini = db.Column(db.String(20), nullable=True)
    nivel_confianza = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    hash_sha256 = db.Column(db.String(64), nullable=False)

    @staticmethod
    def registrar(actor_id, tipo_evento, modulo, version_med_gemini=None, nivel_confianza=None):
        """Crea un registro de auditoría con hash de integridad y lo persiste."""
        timestamp = datetime.now(timezone.utc)
        payload = f"{actor_id}|{tipo_evento}|{modulo}|{timestamp.isoformat()}"
        hash_sha256 = hashlib.sha256(payload.encode()).hexdigest()

        log = LogAuditoria(
            actor_id=actor_id,
            tipo_evento=tipo_evento,
            modulo=modulo,
            version_med_gemini=version_med_gemini,
            nivel_confianza=nivel_confianza,
            timestamp=timestamp,
            hash_sha256=hash_sha256,
        )
        db.session.add(log)
        db.session.commit()
        return log
