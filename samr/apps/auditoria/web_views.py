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
        
    registros = RegistroAuditoria.objects.select_related("usuario").all()

    paginador = Paginator(registros.order_by("-creado_en"), 20)
    pagina = paginador.get_page(request.GET.get("pagina"))
    return render(request, "auditoria/panel.html", {
        "pagina": pagina, "es_auditor": request.user.es_admin or request.user.is_staff,
    })
