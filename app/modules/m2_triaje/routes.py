"""
RF-04 a RF-08 — Módulo M2: Triaje Inteligente y Gestión de Solicitudes.
Referencia: Seq_UC02_Triaje.drawio (ya validado, es el diagrama de referencia
del proyecto — úsalo de guía para nombrar los métodos aquí).

Responsable backend: Antonella (Jira KAN-18)
Responsable modelo de datos: Julio (Jira KAN-17)

TODO (RF-04): endpoint que reciba reportarSintomas(bot/formulario/iot) y cree una Solicitud
TODO (RF-05): invocar MedGeminiEngine.invocarTriaje(solicitud) -> clasificacion XAI
TODO (RF-08): invocar MotorMatching.invocarMatching(nivelRiesgo) -> asignar PersonalMedico
"""

from flask import Blueprint, jsonify

m2_bp = Blueprint("m2_triaje", __name__)


@m2_bp.get("/ping")
def ping():
    return jsonify({"modulo": "M2 - Triaje", "estado": "esqueleto, pendiente de implementar"})
