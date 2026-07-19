"""
RF-01, RF-02, RF-03 — Módulo M1: Registro y Autenticación con MFA.

Las clases y métodos de este archivo siguen EXACTAMENTE los nombres usados
en Seq_UC01_Registro_MFA.drawio (regla del proyecto: nombrar el componente
real, nunca "el sistema"). IESS y ServicioMFA son sistemas externos de
terceros (regla 7): se llaman como funciones auxiliares "reflexivas",
sin tener su propia clase de dominio.
"""

import random
import string
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import current_app

from app import db
from app.models.usuario import Usuario, CodigoMFA, ConsentimientoLOPDP
from app.models.log_auditoria import LogAuditoria


# --- Llamadas externas plegadas (regla 7 del proyecto) ---------------------

def _validar_elegibilidad_iess(cedula: str, afiliacion_iess: str) -> bool:
    """Pliega la llamada externa al IESS. Placeholder: en producción esto
    llamaría a la API real del IESS. Por ahora valida formato únicamente."""
    if not afiliacion_iess:
        return False
    return len(cedula) == 10 and cedula.isdigit()


def _solicitar_envio_codigo_mfa(usuario: Usuario) -> str:
    """Pliega la llamada externa a ServicioMFA. Genera un código de 6
    dígitos y lo 'envía' (en este MVP, se retorna en la respuesta de dev;
    en producción se enviaría por SMS/correo, nunca en el response)."""
    codigo = "".join(random.choices(string.digits, k=6))
    expiracion_min = current_app.config["MFA_CODE_EXPIRATION_MINUTES"]

    registro = CodigoMFA(
        usuario_id=usuario.id,
        codigo=codigo,
        expira_en=datetime.now(timezone.utc) + timedelta(minutes=expiracion_min),
    )
    db.session.add(registro)
    db.session.commit()
    return codigo


# --- FormularioRegistro (pasos 1-3 del diagrama) ----------------------------

class FormularioRegistro:
    @staticmethod
    def ingresar_datos(cedula: str, afiliacion_iess: str, correo: str, password: str):
        """1. ingresarDatos(cedula, afiliacionIESS, correo)"""
        if Usuario.query.filter_by(cedula=cedula).first():
            raise ValueError("Ya existe un usuario registrado con esa cédula.")

        # 2. validarElegibilidadIESS()  (reflexiva, folds IESS)
        if not _validar_elegibilidad_iess(cedula, afiliacion_iess):
            raise ValueError("No se pudo validar la elegibilidad con el IESS.")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        usuario = Usuario(
            cedula=cedula,
            afiliacion_iess=afiliacion_iess,
            correo=correo,
            password_hash=password_hash,
            rol="paciente",
        )
        db.session.add(usuario)
        db.session.commit()

        # 3. solicitarEnvioCodigoMFA()  (reflexiva, folds ServicioMFA)
        codigo_mfa = _solicitar_envio_codigo_mfa(usuario)

        LogAuditoria.registrar(usuario.id, "registro_iniciado", "M1")

        # response: codigoMFAEnviado()
        return usuario, codigo_mfa


# --- Sesion (pasos 4-8 del diagrama) ----------------------------------------

class Sesion:
    @staticmethod
    def digitar_codigo(usuario_id: str, codigo_mfa: str):
        """4. digitarCodigo(codigoMFA)"""
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado.")

        registro = (
            CodigoMFA.query.filter_by(usuario_id=usuario_id, usado=False)
            .order_by(CodigoMFA.id.desc())
            .first()
        )
        if not registro:
            raise ValueError("No hay un código MFA pendiente para este usuario.")

        max_intentos = current_app.config["MAX_INTENTOS_MFA"]
        if registro.intentos >= max_intentos:
            raise ValueError("Se superó el máximo de intentos. Solicita un nuevo código.")

        if datetime.now(timezone.utc) > registro.expira_en.replace(tzinfo=timezone.utc):
            raise ValueError("El código MFA expiró.")

        if registro.codigo != codigo_mfa:
            registro.intentos += 1
            db.session.commit()
            raise ValueError("Código MFA incorrecto.")

        # 5. validarCodigoMFA() + generarTokenOAuth()  (reflexiva)
        registro.usado = True
        token = Sesion._generar_token_oauth(usuario)

        # 6. verificar(pacienteId)  -> ConsentimientoLOPDP
        consentimiento = ConsentimientoLOPDP.query.filter_by(usuario_id=usuario.id).first()
        consentimiento_activo = bool(consentimiento and consentimiento.activo)

        # 7. registrar(actor, tipoEvento, timestamp)  -> LogAuditoria
        db.session.commit()
        LogAuditoria.registrar(usuario.id, "login_mfa_exitoso", "M1")

        # 8. pantallaControl(rol)
        return {
            "token": token,
            "rol": usuario.rol,
            "consentimiento_activo": consentimiento_activo,
        }

    @staticmethod
    def _generar_token_oauth(usuario: Usuario) -> str:
        exp_horas = current_app.config["JWT_EXPIRATION_HOURS"]
        payload = {
            "sub": usuario.id,
            "rol": usuario.rol,
            "exp": datetime.now(timezone.utc) + timedelta(hours=exp_horas),
        }
        return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
