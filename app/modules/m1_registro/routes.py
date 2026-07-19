from flask import Blueprint, jsonify, request

from app.modules.m1_registro.services import FormularioRegistro, Sesion

m1_bp = Blueprint("m1_registro", __name__)


@m1_bp.post("/registro")
def registro():
    """RF-01, RF-02 — Pasos 1-3 del UC-01."""
    data = request.get_json(silent=True) or {}
    requeridos = ["cedula", "afiliacionIESS", "correo", "password"]
    faltantes = [campo for campo in requeridos if not data.get(campo)]
    if faltantes:
        return jsonify({"error": f"Faltan campos: {', '.join(faltantes)}"}), 400

    try:
        usuario, codigo_mfa = FormularioRegistro.ingresar_datos(
            cedula=data["cedula"],
            afiliacion_iess=data["afiliacionIESS"],
            correo=data["correo"],
            password=data["password"],
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "mensaje": "codigoMFAEnviado",
        "usuarioId": usuario.id,
        # OJO: en producción el código NUNCA se devuelve en la respuesta,
        # se envía por SMS/correo. Se expone acá solo para pruebas/demo.
        "codigoMFA_debug": codigo_mfa,
    }), 201


@m1_bp.post("/verificar-mfa")
def verificar_mfa():
    """RF-03 — Pasos 4-8 del UC-01."""
    data = request.get_json(silent=True) or {}
    if not data.get("usuarioId") or not data.get("codigoMFA"):
        return jsonify({"error": "Se requiere usuarioId y codigoMFA"}), 400

    try:
        resultado = Sesion.digitar_codigo(data["usuarioId"], data["codigoMFA"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(resultado), 200
