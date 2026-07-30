"""Vistas web (templates) de la app biometria -- Pantalla 3 (UC-03)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.auditoria.services import RegistroAuditoriaService
from apps.biometria.models import Alerta, DispositivoIoT, LecturaBiometrica
from apps.biometria.queries import obtener_tendencia_agregada



@login_required
def dashboard_biometrico(request):
    """RF-09 a RF-12: grid de vitales, dispositivos y alertas del paciente."""
    dispositivos = DispositivoIoT.objects.filter(paciente=request.user, activo=True)
    lecturas_recientes = (
        LecturaBiometrica.objects.filter(dispositivo__paciente=request.user)
        .select_related("dispositivo")
        .order_by("-tomada_en")[:8]
    )
    alertas = (
        Alerta.objects.filter(paciente=request.user)
        .select_related("lectura")
        .order_by("-creado_en")[:10]
    )
    
    # Preparar datos para Chart.js (graficamos el ultimo tipo de signo registrado)
    import json
    chart_data = None
    if lecturas_recientes:
        ultimo_tipo = lecturas_recientes[0].tipo_signo
        lecturas_chart = (
            LecturaBiometrica.objects.filter(
                dispositivo__paciente=request.user, 
                tipo_signo=ultimo_tipo
            )
            .order_by("-tomada_en")[:15]
        )
        # Invertimos para que la más antigua esté a la izquierda
        lecturas_chart = list(reversed(lecturas_chart))
        chart_data = json.dumps({
            "labels": [l.tomada_en.strftime("%H:%M") for l in lecturas_chart],
            "data": [float(l.valor) for l in lecturas_chart],
            "titulo": lecturas_chart[0].get_tipo_signo_display()
        })

    return render(request, "biometria/dashboard.html", {
        "dispositivos": dispositivos,
        "lecturas": lecturas_recientes,
        "alertas": alertas,
        "chart_data": chart_data,
    })


@login_required
def vincular_dispositivo(request):
    """Permite al paciente registrar y vincular un nuevo dispositivo IoT."""
    from apps.biometria.models import TipoDispositivo
    from apps.biometria.services import DispositivoService
    import secrets

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        tipo = request.POST.get("tipo", "").strip()
        numero_serie = request.POST.get("numero_serie", "").strip()

        if not numero_serie:
            numero_serie = "DEV-" + secrets.token_hex(4).upper()

        try:
            DispositivoService().registrar_dispositivo(
                paciente=request.user,
                nombre=nombre,
                tipo=tipo,
                numero_serie=numero_serie,
            )
            messages.success(request, f"Dispositivo '{nombre}' vinculado con éxito.")
            return redirect("biometria:dashboard")
        except Exception as exc:
            messages.error(request, f"Error al vincular dispositivo: {str(exc)}")

    return render(request, "biometria/vincular_dispositivo.html", {
        "tipos_dispositivo": TipoDispositivo.CHOICES,
    })


@login_required
def atender_alerta(request, alerta_id):
    """RF-11: el paciente o medico marca una alerta como atendida."""
    alerta = get_object_or_404(Alerta, id=alerta_id)
    if alerta.paciente_id != request.user.id and not (request.user.es_medico or request.user.es_admin):
        messages.error(request, "No tienes acceso a esta alerta.")
        return redirect("biometria:dashboard")

    alerta.atendida = True
    alerta.save(update_fields=["atendida", "actualizado_en"])
    RegistroAuditoriaService().registrar(
        usuario=request.user, accion="alerta_atendida",
        ruta="/biometria/alertas/{0}/atender/".format(alerta_id), codigo_estado=200,
    )
    messages.success(request, "Alerta marcada como atendida.")
    return redirect("biometria:dashboard")


@login_required
def registrar_lectura(request):
    """RF-09/RF-10: simula la llegada de una lectura desde un dispositivo IoT real."""
    from apps.biometria.services import LecturaService, DispositivoService
    import secrets
    
    if request.method == "POST":
        tipo_signo = request.POST.get("tipo_signo")
        valor = request.POST.get("valor")
        dispositivo_id = request.POST.get("dispositivo_id")

        dispositivo = None
        if dispositivo_id:
            dispositivo = DispositivoIoT.objects.filter(id=dispositivo_id, paciente=request.user, activo=True).first()

        if not dispositivo:
            dispositivo = DispositivoIoT.objects.filter(paciente=request.user, activo=True).first()

        if not dispositivo:
            dispositivo = DispositivoService().registrar_dispositivo(
                paciente=request.user,
                nombre="Dispositivo IoT Principal",
                tipo="PULSERA",
                numero_serie="DEV-" + secrets.token_hex(4).upper(),
            )
            
        try:
            LecturaService().registrar_lectura(
                dispositivo=dispositivo,
                tipo_signo=tipo_signo,
                valor=float(valor)
            )
            messages.success(request, f"Lectura registrada con éxito en '{dispositivo.nombre}'.")
        except Exception as e:
            messages.error(request, f"Error al registrar lectura: {str(e)}")
            
    return redirect("biometria:dashboard")
