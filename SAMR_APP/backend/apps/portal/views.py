"""Vistas de la app portal (Pantalla 1: Login y Registro con MFA)."""
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from shared.exceptions import ReglaNegocioError
from apps.usuarios.models import Usuario
from apps.portal.forms import LoginForm, MFAForm, RegistroForm
from apps.portal.services import FormularioRegistro, Sesion


def _ip_cliente(request):
    return request.META.get("REMOTE_ADDR")


def registro_view(request):
    if request.user.is_authenticated:
        return redirect("portal:dashboard")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                usuario, codigo = FormularioRegistro().ingresar_datos(
                    datos=form.cleaned_data,
                    dispositivo_iot=form.cleaned_data.get("dispositivo_iot") or None,
                    ip=_ip_cliente(request),
                )
            except ReglaNegocioError as exc:
                form.add_error(None, exc.message)
            else:
                request.session["mfa_usuario_id"] = usuario.id
                request.session["mfa_origen"] = "registro"
                messages.success(
                    request,
                    "Cuenta creada. Enviamos un codigo de verificacion a tu dispositivo.",
                )
                if request.META.get("DEBUG_MFA", True):
                    messages.info(request, "Codigo de prueba (solo en desarrollo): {0}".format(codigo))
                return redirect("portal:verificar_mfa")
    else:
        form = RegistroForm()

    return render(request, "portal/registro.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("portal:dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                usuario = Sesion.autenticar_password(
                    form.cleaned_data["email"], form.cleaned_data["password"]
                )
            except ReglaNegocioError as exc:
                form.add_error(None, exc.message)
            else:
                codigo = Sesion.solicitar_envio_codigo_mfa(usuario)
                request.session["mfa_usuario_id"] = usuario.id
                request.session["mfa_origen"] = "login"
                messages.info(request, "Enviamos un codigo de verificacion a tu dispositivo.")
                if request.META.get("DEBUG_MFA", True):
                    messages.info(request, "Codigo de prueba (solo en desarrollo): {0}".format(codigo))
                return redirect("portal:verificar_mfa")
    else:
        form = LoginForm()

    return render(request, "portal/login.html", {"form": form})


def verificar_mfa_view(request):
    usuario_id = request.session.get("mfa_usuario_id")
    if not usuario_id:
        messages.error(request, "Tu sesion de verificacion expiro. Inicia sesion de nuevo.")
        return redirect("portal:login")

    usuario = Usuario.objects.filter(id=usuario_id).first()
    if usuario is None:
        request.session.pop("mfa_usuario_id", None)
        return redirect("portal:login")

    if request.method == "POST":
        form = MFAForm(request.POST)
        if form.is_valid():
            try:
                Sesion.digitar_codigo(usuario, form.cleaned_data["codigo"])
            except ReglaNegocioError as exc:
                form.add_error(None, exc.message)
            else:
                django_login(request, usuario)
                request.session.pop("mfa_usuario_id", None)
                request.session.pop("mfa_origen", None)
                messages.success(request, "Verificacion exitosa. Bienvenido(a), {0}.".format(
                    usuario.nombre_completo
                ))
                return redirect("portal:dashboard")
    else:
        form = MFAForm()

    return render(request, "portal/verificar_mfa.html", {"form": form, "usuario": usuario})


def reenviar_mfa_view(request):
    usuario_id = request.session.get("mfa_usuario_id")
    if not usuario_id:
        return redirect("portal:login")
    usuario = Usuario.objects.filter(id=usuario_id).first()
    if usuario is None:
        return redirect("portal:login")

    try:
        codigo = Sesion.reenviar_codigo_mfa(usuario)
    except ReglaNegocioError as exc:
        messages.error(request, exc.message)
    else:
        messages.info(request, "Reenviamos el codigo de verificacion.")
        if request.META.get("DEBUG_MFA", True):
            messages.info(request, "Codigo de prueba (solo en desarrollo): {0}".format(codigo))
    return redirect("portal:verificar_mfa")


@login_required(login_url="portal:login")
def dashboard_view(request):
    context = {"usuario": request.user}
    if request.user.rol == "MEDICO":
        from apps.teleconsulta.models import Teleconsulta
        hoy = timezone.now().date()
        citas = Teleconsulta.objects.filter(
            medico=request.user, 
            estado__in=['PROGRAMADA', 'EN_CURSO']
        )
        context["citas_hoy"] = citas.filter(fecha_programada__date=hoy).count()
        context["proximas_citas"] = citas.order_by("fecha_programada")[:3]
        
    return render(request, "portal/dashboard.html", context)


def logout_view(request):
    django_logout(request)
    messages.info(request, "Sesion cerrada correctamente.")
    return redirect("portal:login")
