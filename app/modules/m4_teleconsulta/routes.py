"""
RF-13 a RF-16 — Módulo M4: Teleconsulta y Atención Médica.
Referencia: Seq_UC04_Teleconsulta.drawio (corregido: se agregó
CentroAsistencia como participante propio).

Responsable backend: Antonella (Jira KAN-30)
Responsable modelo de datos: Julio (Jira KAN-29)

TODO (RF-13): endpoint iniciar(pacienteId) -> Teleconsulta.establecerTransmision()
TODO (RF-13): Teleconsulta.obtenerHistorialClinico()
TODO (RF-14): invocar MedGeminiEngine.solicitarSugerenciaXAI(contexto)
TODO (RF-14): RecetaDigital.generarOrden() + emitirFirmada() (firma: ver Alisson, seguridad)
TODO (RF-15): activarDerivacion(datosUrgentes) -> CentroAsistencia [caso crítico]
TODO (RF-16): flujo alterno de rechazo y reasignación (diagrama aparte, no incluido en UC-04)
"""

from flask import Blueprint, jsonify

m4_bp = Blueprint("m4_teleconsulta", __name__)


@m4_bp.get("/ping")
def ping():
    return jsonify({"modulo": "M4 - Teleconsulta", "estado": "esqueleto, pendiente de implementar"})
