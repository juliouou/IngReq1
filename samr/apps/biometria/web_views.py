"""Vistas web (templates) de la app biometria -- Pantalla 3 (UC-03)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.auditoria.services import RegistroAuditoriaService
from apps.biometria.models import Alerta, DispositivoIoT, LecturaBiometrica


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
    return render(request, "biometria/dashboard.html", {
        "dispositivos": dispositivos,
        "lecturas": lecturas_recientes,
        "alertas": alertas,
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
