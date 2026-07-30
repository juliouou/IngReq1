"""Admin de la app auditoria."""
from django.contrib import admin

from apps.auditoria.models import RegistroAuditoria


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "accion", "ruta", "codigo_estado", "creado_en")
    list_filter = ("accion", "codigo_estado")
    search_fields = ("ruta", "request_id", "usuario__email")
    readonly_fields = (
        "usuario", "accion", "ruta", "codigo_estado",
        "request_id", "ip", "creado_en", "actualizado_en",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
