"""Vistas web (templates) de la app teleconsulta -- Pantalla 4 (UC-04)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from shared.exceptions import SamrException
from apps.teleconsulta.models import Teleconsulta, HistorialClinico
from apps.teleconsulta.services import RecetaService, TeleconsultaService
from apps.biometria.models import DispositivoIoT, Alerta


@login_required
def lista_teleconsultas(request):
    """Lista las teleconsultas del usuario (como medico o como paciente)."""
    qs = Teleconsulta.objects.filter(
        Q(medico=request.user) | Q(paciente=request.user)
    ).select_related("medico", "paciente", "receta").order_by("-fecha_programada")
    return render(request, "teleconsulta/lista.html", {"teleconsultas": qs})


@login_required
def detalle_teleconsulta(request, teleconsulta_id):
    """RF-13, RF-14, RF-15: ver detalle, finalizar y emitir receta."""
    tc = get_object_or_404(
        Teleconsulta.objects.select_related("medico", "paciente", "receta"), id=teleconsulta_id
    )
    if request.user.id not in (tc.medico_id, tc.paciente_id) and not request.user.es_admin:
        messages.error(request, "No tienes acceso a esta teleconsulta.")
        return redirect("teleconsulta:lista")

    es_medico_de_esta_consulta = request.user.id == tc.medico_id

    # Si el paciente entra y hay receta sin leer, marcarla como leída
    if request.user.id == tc.paciente_id and hasattr(tc, "receta") and tc.receta and not tc.receta.leida:
        tc.receta.leida = True
        tc.receta.save(update_fields=["leida"])

    if request.method == "POST" and es_medico_de_esta_consulta:
        accion = request.POST.get("accion")
        try:
            if accion == "iniciar":
                TeleconsultaService().iniciar(tc)
                messages.success(request, "Teleconsulta iniciada.")
            elif accion == "rechazar":
                motivo = request.POST.get("motivo", "")
                nueva_tc = TeleconsultaService().rechazar_y_reasignar(tc, request.user, motivo)
                nombre_nuevo = nueva_tc.medico.nombre_completo or nueva_tc.medico.email
                messages.success(request, f"Teleconsulta rechazada y reasignada exitosamente al Dr(a). {nombre_nuevo}.")
                return redirect("teleconsulta:lista")
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

    # Datos de contexto clínico para el médico durante la consulta
    historial_clinico = []
    dispositivos_iot = []
    lecturas_recientes = []
    alertas_pendientes = []

    if es_medico_de_esta_consulta:
        historial_clinico = HistorialClinico.objects.filter(
            paciente=tc.paciente
        ).order_by("-creado_en")[:5]

        dispositivos_iot = DispositivoIoT.objects.filter(
            paciente=tc.paciente, activo=True
        )

        for disp in dispositivos_iot:
            ultima = disp.lecturas.order_by("-tomada_en").first()
            if ultima:
                lecturas_recientes.append(ultima)

        alertas_pendientes = Alerta.objects.filter(
            paciente=tc.paciente, atendida=False
        ).select_related("lectura__dispositivo").order_by("-creado_en")[:5]

    historial_de_esta_consulta = HistorialClinico.objects.filter(teleconsulta=tc).first()

    return render(request, "teleconsulta/detalle.html", {
        "tc": tc,
        "es_medico": es_medico_de_esta_consulta,
        "historial_clinico": historial_clinico,
        "historial_de_esta_consulta": historial_de_esta_consulta,
        "dispositivos_iot": dispositivos_iot,
        "lecturas_recientes": lecturas_recientes,
        "alertas_pendientes": alertas_pendientes,
    })
