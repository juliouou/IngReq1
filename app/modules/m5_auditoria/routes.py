"""
RF-17 a RF-20 — Módulo M5: Acceso a Registros de Auditoría y Cumplimiento.
Referencia: Seq_UC05_Auditoria.drawio (ya validado, no necesitó correcciones).

Responsable backend: Antonella (Jira KAN-36)
Responsable modelo de datos: Julio (Jira KAN-35)
Responsable seguridad/cifrado: Alisson (Jira KAN-38)

TODO (RF-17): PoliticaCifrado.descifrar(registros, AES256) — solo rol auditor
TODO (RF-18): exponer estado de ConsentimientoLOPDP por usuario
TODO (RF-20): endpoint de solo lectura sobre LogAuditoria (ya modelado, ver app/models/log_auditoria.py)
"""

from flask import Blueprint, jsonify

from app.models.log_auditoria import LogAuditoria

m5_bp = Blueprint("m5_auditoria", __name__)


@m5_bp.get("/logs")
def listar_logs():
    """RF-20: lectura de logs de auditoría. TODO Alisson: restringir a rol=auditor."""
    logs = LogAuditoria.query.order_by(LogAuditoria.timestamp.desc()).limit(50).all()
    return jsonify([
        {
            "id": log.id,
            "actorId": log.actor_id,
            "tipoEvento": log.tipo_evento,
            "modulo": log.modulo,
            "timestamp": log.timestamp.isoformat(),
            "hashSHA256": log.hash_sha256,
        }
        for log in logs
    ])
