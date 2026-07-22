"""Vistas web (templates) de la app auditoria -- Pantalla de auditoria (UC-05)."""
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect, render

from apps.auditoria.models import RegistroAuditoria


@login_required
def panel_auditoria(request):
    """RF-20: solo administradores/auditores ven el log completo."""
    if not (request.user.es_admin or request.user.rol == 'ADMINISTRATIVO' or request.user.is_staff):
        messages.error(request, "No tienes permiso para acceder al panel de auditoría.")
        return redirect("portal:dashboard")
        
    q = request.GET.get("q", "").strip()
    registros = RegistroAuditoria.objects.select_related("usuario").all()

    if q:
        from apps.triaje.models import SolicitudAtencion
        from apps.teleconsulta.models import Teleconsulta
        from django.db.models import Q

        solicitud = SolicitudAtencion.objects.filter(Q(codigo__iexact=q) | Q(codigo__icontains=q)).first()
        teleconsulta = Teleconsulta.objects.filter(Q(codigo__iexact=q) | Q(codigo__icontains=q)).first()

        q_filters = Q(ruta__icontains=q) | Q(request_id__icontains=q) | Q(accion__icontains=q) | Q(usuario__email__icontains=q)

        if solicitud:
            q_filters |= Q(ruta__icontains=f"/triaje/{solicitud.id}/")
            for tc_item in solicitud.teleconsultas.all():
                q_filters |= Q(ruta__icontains=f"/teleconsulta/{tc_item.id}/")
                q_filters |= Q(ruta__icontains=f"/ws/teleconsulta/{tc_item.id}/")

        if teleconsulta:
            q_filters |= Q(ruta__icontains=f"/teleconsulta/{teleconsulta.id}/")
            q_filters |= Q(ruta__icontains=f"/ws/teleconsulta/{teleconsulta.id}/")
            if teleconsulta.solicitud_id:
                q_filters |= Q(ruta__icontains=f"/triaje/{teleconsulta.solicitud_id}/")

        registros = registros.filter(q_filters).order_by("creado_en")
    else:
        registros = registros.order_by("-creado_en")

    paginador = Paginator(registros, 25)
    pagina = paginador.get_page(request.GET.get("pagina"))
    return render(request, "auditoria/panel.html", {
        "pagina": pagina,
        "es_auditor": request.user.es_admin or request.user.is_staff,
        "q": q,
    })
