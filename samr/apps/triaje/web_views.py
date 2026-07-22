"""Vistas web (templates) de la app triaje -- Pantalla 2 (UC-02)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.exceptions import SamrException
from core.motor_ia import clasificar_sintomas
from apps.auditoria.services import RegistroAuditoriaService
from apps.triaje.models import SolicitudAtencion
from apps.triaje.services import SolicitudService


@login_required
def solicitudes_lista(request):
    """RF-08: panel dinamico de estados de las solicitudes del paciente."""
    solicitudes = (
        SolicitudAtencion.objects.filter(paciente=request.user)
        .select_related("evaluacion")
        .order_by("-creado_en")
    )
    return render(request, "triaje/lista.html", {"solicitudes": solicitudes})


@login_required
def nueva_solicitud(request):
    """RF-04, RF-05: el paciente describe sintomas y Med-Gemini clasifica."""
    resultado = None
    if request.method == "POST":
        sintomas = request.POST.get("sintomas", "").strip()
        motivo = request.POST.get("motivo", "").strip() or "Consulta general"
        if not sintomas:
            messages.error(request, "Describe tus sintomas antes de enviar la solicitud.")
        else:
            try:
                solicitud = SolicitudService().crear_solicitud(
                    paciente=request.user, motivo=motivo, sintomas=sintomas
                )
                # Med-Gemini (stub): clasificacion automatica RF-05
                resultado = clasificar_sintomas(sintomas)
                SolicitudService().registrar_triaje(
                    solicitud,
                    evaluado_por=None,
                    nivel_urgencia=resultado["nivel_urgencia"],
                    observaciones=resultado["explicacion_xai"],
                )
                RegistroAuditoriaService().registrar(
                    usuario=request.user, accion="solicitud_clasificada",
                    ruta="/triaje/nueva/", codigo_estado=201,
                )
                messages.success(request, "Solicitud enviada y clasificada.")
                return redirect("triaje:detalle", solicitud_id=solicitud.id)
            except SamrException as exc:
                messages.error(request, exc.message)

    return render(request, "triaje/nueva.html", {"resultado": resultado})


@login_required
def detalle_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(
        SolicitudAtencion.objects.select_related("evaluacion"), id=solicitud_id
    )
    if solicitud.paciente_id != request.user.id and not request.user.es_admin and not request.user.es_medico:
        messages.error(request, "No tienes acceso a esta solicitud.")
        return redirect("triaje:lista")
    return render(request, "triaje/detalle.html", {"solicitud": solicitud})
