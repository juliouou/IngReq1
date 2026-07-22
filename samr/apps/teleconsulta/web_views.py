"""Vistas web (templates) de la app teleconsulta -- Pantalla 4 (UC-04)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.exceptions import SamrException
from apps.teleconsulta.models import Teleconsulta
from apps.teleconsulta.services import RecetaService, TeleconsultaService


@login_required
def lista_teleconsultas(request):
    """Lista las teleconsultas del usuario (como medico o como paciente)."""
    qs = Teleconsulta.objects.filter(
        Q(medico=request.user) | Q(paciente=request.user)
    ).select_related("medico", "paciente").order_by("-fecha_programada")
    return render(request, "teleconsulta/lista.html", {"teleconsultas": qs})


@login_required
def detalle_teleconsulta(request, teleconsulta_id):
    """RF-13, RF-14, RF-15: ver detalle, finalizar y emitir receta."""
    tc = get_object_or_404(
        Teleconsulta.objects.select_related("medico", "paciente"), id=teleconsulta_id
    )
    if request.user.id not in (tc.medico_id, tc.paciente_id) and not request.user.es_admin:
        messages.error(request, "No tienes acceso a esta teleconsulta.")
        return redirect("teleconsulta:lista")

    es_medico_de_esta_consulta = request.user.id == tc.medico_id

    if request.method == "POST" and es_medico_de_esta_consulta:
        accion = request.POST.get("accion")
        try:
            if accion == "iniciar":
                TeleconsultaService().iniciar(tc)
                messages.success(request, "Teleconsulta iniciada.")
            elif accion == "finalizar":
                TeleconsultaService().finalizar(
                    tc,
                    diagnostico=request.POST.get("diagnostico", ""),
                    notas=request.POST.get("notas", ""),
                )
                messages.success(request, "Teleconsulta finalizada y agregada al historial clinico.")
            elif accion == "emitir_receta":
                medicamentos = []
                nombres = request.POST.getlist("medicamento")
                dosis = request.POST.getlist("dosis")
                for nombre, dosis_val in zip(nombres, dosis):
                    if nombre.strip():
                        medicamentos.append({
                            "medicamento": nombre, "dosis": dosis_val,
                            "frecuencia": request.POST.get("frecuencia", ""),
                            "duracion": request.POST.get("duracion", ""),
                        })
                RecetaService().emitir(
                    tc,
                    indicaciones_generales=request.POST.get("indicaciones", ""),
                    medicamentos=medicamentos,
                )
                messages.success(request, "Receta digital emitida.")
        except SamrException as exc:
            messages.error(request, exc.message)
        return redirect("teleconsulta:detalle", teleconsulta_id=tc.id)

    return render(request, "teleconsulta/detalle.html", {
        "tc": tc, "es_medico": es_medico_de_esta_consulta,
    })
