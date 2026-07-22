"""
Servicios de la app portal.

FormularioRegistro y Sesion (nombres tomados directo de
Seq_UC01_Registro_MFA.drawio, el diagrama corregido) orquestan a los
servicios que ya existen en otras apps (UsuarioService, DispositivoService,
RegistroAuditoriaService) en vez de duplicar su logica.
"""
import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone

from core.exceptions import ReglaNegocioError
from apps.usuarios.models import Usuario
from apps.usuarios.services import UsuarioService
from apps.biometria.models import TipoDispositivo
from apps.biometria.services import DispositivoService
from apps.auditoria.services import RegistroAuditoriaService
from apps.portal.models import CodigoMFA, ConsentimientoLOPDP

MFA_EXPIRACION_MINUTOS = 5
MFA_MAX_INTENTOS = 3
MFA_REENVIO_SEGUNDOS = 20  # RNF: evita spam de reenvio (rate limit simple)


def _validar_elegibilidad_iess(cedula, afiliacion_iess):
    """
    Pliega la llamada externa al IESS (regla 7 del proyecto: sin tabla ni
    clase propia). Valida formato unicamente -- en produccion esto llamaria
    a la API real del IESS/MSP.
    """
    if not afiliacion_iess:
        return False
    return bool(cedula) and len(cedula) == 10 and cedula.isdigit()


class FormularioRegistro:
    """Pasos 1-3 del diagrama UC-01."""

    def __init__(self):
        self.usuario_service = UsuarioService()
        self.dispositivo_service = DispositivoService()
        self.auditoria_service = RegistroAuditoriaService()

    def ingresar_datos(self, datos, dispositivo_iot=None, ip=None):
        """1. ingresarDatos(...) -> 2. validarElegibilidadIESS() (reflexiva)."""
        cedula = datos.get("cedula")
        afiliacion_iess = datos.get("afiliacion_iess")

        if not _validar_elegibilidad_iess(cedula, afiliacion_iess):
            raise ReglaNegocioError(
                "No se pudo validar la elegibilidad con el IESS. "
                "Revisa la cedula y el numero de afiliacion."
            )

        usuario = self.usuario_service.registrar(
            email=datos["email"],
            password=datos["password"],
            nombres=datos["nombres"],
            apellidos=datos["apellidos"],
            cedula=cedula,
            telefono=datos.get("telefono", ""),
            afiliacion_iess=afiliacion_iess,
            rol="PACIENTE",
        )
        # PerfilPaciente se crea solo via el signal post_save de Usuario
        # (ver apps/usuarios/signals.py) -- no duplicar aqui.

        # Vinculo opcional de dispositivo IoT ("vincular mas tarde" = None)
        if dispositivo_iot:
            nombre_dispositivo = dict(TipoDispositivo.CHOICES).get(dispositivo_iot, dispositivo_iot)
            self.dispositivo_service.registrar_dispositivo(
                paciente=usuario,
                nombre=nombre_dispositivo,
                tipo=dispositivo_iot,
                numero_serie="SN-{0}-{1}".format(usuario.id, random.randint(1000, 9999)),
            )

        # Consentimiento LOPDP -- obligatorio para llegar hasta aqui (el
        # formulario ya valido que el checkbox este marcado)
        ConsentimientoLOPDP.objects.create(
            usuario=usuario, activo=True, ip=ip, aceptado_en=timezone.now()
        )

        self.auditoria_service.registrar(
            usuario=usuario, accion="registro_completado", ruta="/portal/registro/",
            codigo_estado=201, ip=ip,
        )

        codigo = Sesion.solicitar_envio_codigo_mfa(usuario)
        return usuario, codigo


class Sesion:
    """Pasos 4-8 del diagrama UC-01."""

    @staticmethod
    def solicitar_envio_codigo_mfa(usuario):
        """3. solicitarEnvioCodigoMFA() (reflexiva, pliega ServicioMFA)."""
        codigo = "{0:06d}".format(random.randint(0, 999999))
        CodigoMFA.objects.create(
            usuario=usuario,
            codigo=codigo,
            expira_en=timezone.now() + timedelta(minutes=MFA_EXPIRACION_MINUTOS),
        )
        # En produccion: enviar por SMS/correo. En dev, se muestra en pantalla.
        return codigo

    @staticmethod
    def autenticar_password(email, password):
        """Paso previo al MFA cuando el usuario ya existe (login normal)."""
        usuario = authenticate(username=email, password=password)
        if usuario is None:
            raise ReglaNegocioError("Correo o contrasena incorrectos.")
        return usuario

    @staticmethod
    def reenviar_codigo_mfa(usuario):
        ultimo = CodigoMFA.objects.filter(usuario=usuario).order_by("-creado_en").first()
        if ultimo and (timezone.now() - ultimo.creado_en).total_seconds() < MFA_REENVIO_SEGUNDOS:
            raise ReglaNegocioError(
                "Espera unos segundos antes de solicitar otro codigo."
            )
        return Sesion.solicitar_envio_codigo_mfa(usuario)

    @staticmethod
    def digitar_codigo(usuario, codigo_ingresado):
        """4-5. digitarCodigo() + validarCodigoMFA() (reflexiva)."""
        registro = (
            CodigoMFA.objects.filter(usuario=usuario, usado=False)
            .order_by("-creado_en")
            .first()
        )
        if registro is None:
            raise ReglaNegocioError("No hay un codigo MFA pendiente. Solicita uno nuevo.")

        if registro.intentos >= MFA_MAX_INTENTOS:
            raise ReglaNegocioError("Se supero el maximo de intentos. Solicita un nuevo codigo.")

        if registro.expirado:
            raise ReglaNegocioError("El codigo MFA expiro. Solicita uno nuevo.")

        if registro.codigo != codigo_ingresado:
            registro.intentos += 1
            registro.save(update_fields=["intentos", "actualizado_en"])
            raise ReglaNegocioError("Codigo MFA incorrecto.")

        registro.usado = True
        registro.save(update_fields=["usado", "actualizado_en"])

        # 6. verificar(pacienteId) -> ConsentimientoLOPDP
        consentimiento = ConsentimientoLOPDP.objects.filter(usuario=usuario).first()
        consentimiento_activo = bool(consentimiento and consentimiento.activo)

        # 7. registrar(actor, tipoEvento, timestamp) -> LogAuditoria
        RegistroAuditoriaService().registrar(
            usuario=usuario, accion="login_mfa_exitoso", ruta="/portal/verificar-mfa/",
            codigo_estado=200,
        )

        return consentimiento_activo
