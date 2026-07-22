"""Vistas web (templates) de la app triaje -- Pantalla 2 (UC-02)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.exceptions import SamrException
from core.motor_ia import clasificar_sintomas, responder_chat
from apps.auditoria.services import RegistroAuditoriaService
from apps.triaje.models import SolicitudAtencion, MensajeChat, TipoOrigenSolicitud, NivelUrgencia
from apps.triaje.services import SolicitudService
from apps.biometria.models import DispositivoIoT, LecturaBiometrica, Alerta, NivelAlerta


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
def chat_nuevo(request):
    """RF-04: Inicia un nuevo chat conversacional, limpiando la sesion."""
    request.session.pop("chat_solicitud_id", None)
    return redirect("triaje:chat")


@login_required
def chat_triaje(request):
    """RF-04: Maneja el chat conversacional activo."""
    solicitud_id = request.session.get("chat_solicitud_id")
    
    if not solicitud_id:
        if request.method == "POST":
            texto = request.POST.get("texto", "").strip()
            if texto:
                solicitud = SolicitudService().crear_solicitud(
                    paciente=request.user, motivo="Consulta por chat", sintomas="-"
                )
                request.session["chat_solicitud_id"] = solicitud.id
                MensajeChat.objects.create(solicitud=solicitud, autor="PACIENTE", texto=texto)
                
                res = responder_chat("", texto, 0)
                MensajeChat.objects.create(solicitud=solicitud, autor="BOT", texto=res["texto_respuesta"])
                
                if res["listo_para_clasificar"]:
                    _completar_triaje(solicitud, texto, res["resultado"], request)
            return redirect("triaje:chat")
        
        return render(request, "triaje/chat.html", {"mensajes": [], "solicitud": None})
    
    solicitud = get_object_or_404(SolicitudAtencion, id=solicitud_id, paciente=request.user)
    
    if request.method == "POST" and not hasattr(solicitud, "evaluacion"):
        texto = request.POST.get("texto", "").strip()
        if texto:
            mensajes_previos = list(solicitud.mensajes.order_by("creado_en"))
            historial = " ".join([m.texto for m in mensajes_previos if m.autor == "PACIENTE"])
            turno = sum(1 for m in mensajes_previos if m.autor == "PACIENTE")
            
            MensajeChat.objects.create(solicitud=solicitud, autor="PACIENTE", texto=texto)
            
            res = responder_chat(historial, texto, turno)
            MensajeChat.objects.create(solicitud=solicitud, autor="BOT", texto=res["texto_respuesta"])
            
            if res["listo_para_clasificar"]:
                texto_completo = historial + " " + texto
                _completar_triaje(solicitud, texto_completo, res["resultado"], request)
                
        return redirect("triaje:chat")

    mensajes = solicitud.mensajes.order_by("creado_en")
    return render(request, "triaje/chat.html", {"mensajes": mensajes, "solicitud": solicitud})


def _completar_triaje(solicitud, texto_completo, resultado, request):
    """Helper para registrar triaje al terminar chat."""
    solicitud.sintomas = texto_completo
    solicitud.save()
    SolicitudService().registrar_triaje(
        solicitud,
        evaluado_por=None,
        nivel_urgencia=resultado["nivel_urgencia"],
        observaciones=resultado["explicacion_xai"],
    )
    RegistroAuditoriaService().registrar(
        usuario=request.user, accion="solicitud_clasificada",
        ruta="/triaje/chat/", codigo_estado=201,
    )


@login_required
def chat_ver(request, solicitud_id):
    """RF-04: Ver el historial de chat de una solicitud ya clasificada."""
    solicitud = get_object_or_404(
        SolicitudAtencion.objects.select_related("evaluacion"), id=solicitud_id
    )
    if solicitud.paciente_id != request.user.id and not request.user.es_admin and not request.user.es_medico:
        messages.error(request, "No tienes acceso a este chat.")
        return redirect("triaje:lista")
    
    mensajes = solicitud.mensajes.order_by("creado_en")
    return render(request, "triaje/chat.html", {"mensajes": mensajes, "solicitud": solicitud})


@login_required
def detalle_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(
        SolicitudAtencion.objects.select_related("evaluacion"), id=solicitud_id
    )
    if solicitud.paciente_id != request.user.id and not request.user.es_admin and not request.user.es_medico:
        messages.error(request, "No tienes acceso a esta solicitud.")
        return redirect("triaje:lista")
    return render(request, "triaje/detalle.html", {"solicitud": solicitud})


@login_required
@require_POST
def escalar_a_humano(request, solicitud_id):
    """RF-04: Escalar la clasificacion a un agente humano."""
    solicitud = get_object_or_404(SolicitudAtencion, id=solicitud_id, paciente=request.user)
    if hasattr(solicitud, "evaluacion"):
        RegistroAuditoriaService().registrar(
            usuario=request.user, accion="escala_triaje_humano",
            ruta=request.path, codigo_estado=200,
        )
        messages.success(request, "Tu solicitud ha sido escalada para revisión manual por un médico humano.")
    return redirect("triaje:detalle", solicitud_id=solicitud.id)


@login_required
def solicitar_emergencia_manual(request):
    """Flujo A: Emergencia manual (sin IA)."""
    solicitud = SolicitudService().crear_solicitud(
        paciente=request.user,
        motivo="Emergencia solicitada manualmente por el paciente",
        sintomas="Emergencia manual sin diálogo de IA",
        tipo_origen=TipoOrigenSolicitud.EMERGENCIA_MANUAL,
    )
    SolicitudService().registrar_triaje(
        solicitud,
        evaluado_por=None,
        nivel_urgencia=NivelUrgencia.EMERGENCIA,
        observaciones="Emergencia solicitada directamente por el paciente.",
    )
    RegistroAuditoriaService().registrar(
        usuario=request.user,
        accion="EMERGENCIA",
        ruta="/triaje/emergencia/",
        codigo_estado=201,
    )
    messages.success(request, "Se ha registrado su emergencia y notificado al personal médico de inmediato.")
    return redirect("triaje:detalle", solicitud_id=solicitud.id)


@login_required
def solicitar_alerta_iot(request):
    """Flujo B: Alerta generada por IoT."""
    dispositivos = DispositivoIoT.objects.filter(paciente=request.user, activo=True)
    if not dispositivos.exists():
        messages.error(request, "No tienes dispositivos IoT vinculados o activos.")
        return redirect("triaje:lista")

    alertas_activas = Alerta.objects.filter(paciente=request.user, atendida=False).select_related('lectura')
    
    if alertas_activas.exists():
        alertas = list(alertas_activas.order_by("-creado_en"))
        descripciones = []
        for a in alertas:
            descripciones.append(
                f"Alerta: {a.mensaje} - Signo: {a.lectura.tipo_signo} con valor {a.lectura.valor} {a.lectura.unidad} (Nivel: {a.nivel})"
            )
        sintomas = "Alertas biométricas activas detectadas por dispositivo IoT:\n" + "\n".join(descripciones)
        
        alerta_reciente = alertas[0]
        if alerta_reciente.nivel == NivelAlerta.CRITICA:
            nivel_urgencia = NivelUrgencia.EMERGENCIA
        else:
            nivel_urgencia = NivelUrgencia.MUY_URGENTE
        
        alertas_activas.update(atendida=True)
    else:
        lecturas_recientes = LecturaBiometrica.objects.filter(
            dispositivo__in=dispositivos
        ).order_by("-tomada_en")
        
        lecturas_fuera = list(lecturas_recientes.filter(fuera_de_rango=True)[:5])
        if lecturas_fuera:
            descripciones = []
            for l in lecturas_fuera:
                descripciones.append(
                    f"Signo fuera de rango: {l.tipo_signo} con valor {l.valor} {l.unidad} (Tomada en: {l.tomada_en.strftime('%Y-%m-%d %H:%M:%S') if l.tomada_en else ''})"
                )
            sintomas = "Lecturas biométricas fuera de rango detectadas por dispositivo IoT:\n" + "\n".join(descripciones)
            nivel_urgencia = NivelUrgencia.MUY_URGENTE
        else:
            ultima_lectura = lecturas_recientes.first()
            if ultima_lectura:
                sintomas = f"Última lectura biométrica: {ultima_lectura.tipo_signo} = {ultima_lectura.valor} {ultima_lectura.unidad}. Lecturas dentro del rango normal."
            else:
                sintomas = "No hay lecturas biométricas disponibles."
            nivel_urgencia = NivelUrgencia.MUY_URGENTE

    solicitud = SolicitudService().crear_solicitud(
        paciente=request.user,
        motivo="Alerta generada automáticamente por dispositivo IoT",
        sintomas=sintomas,
        tipo_origen=TipoOrigenSolicitud.ALERTA_IOT,
    )
    SolicitudService().registrar_triaje(
        solicitud,
        evaluado_por=None,
        nivel_urgencia=nivel_urgencia,
        observaciones="Triaje automático generado a partir de datos/alertas de dispositivos IoT vinculados.",
    )
    RegistroAuditoriaService().registrar(
        usuario=request.user,
        accion="ALERTA_IOT",
        ruta="/triaje/alerta-iot/",
        codigo_estado=201,
    )
    messages.success(request, "Se ha generado una solicitud de atención a partir de sus lecturas biométricas.")
    return redirect("triaje:detalle", solicitud_id=solicitud.id)
