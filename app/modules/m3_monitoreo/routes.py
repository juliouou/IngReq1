"""
RF-09 a RF-12 — Módulo M3: Monitoreo Biométrico Predictivo Continuo.
Referencia: Seq_UC03_Monitoreo.drawio (corregido: DispositivoIoT ->
CapturaBiometrica -> MedGeminiEngine -> BotConversacional -> Paciente/
PersonalMedico -> CentroAsistencia).

Responsable backend: Antonella (Jira KAN-24)
Responsable modelo de datos: Julio (Jira KAN-23)

TODO (RF-09): endpoint que reciba transmitirLecturas(EKG, EEG, SpO2) del DispositivoIoT
TODO (RF-10): invocar MedGeminiEngine.invocarDeteccion(lecturas) -> generar AlertaPredictivaXAI
TODO (RF-11, RF-12): notificar BotConversacional -> Paciente, y PersonalMedico -> CentroAsistencia
"""

from flask import Blueprint, jsonify

m3_bp = Blueprint("m3_monitoreo", __name__)


@m3_bp.get("/ping")
def ping():
    return jsonify({"modulo": "M3 - Monitoreo", "estado": "esqueleto, pendiente de implementar"})
