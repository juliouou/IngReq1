"""Admin de la app triaje."""
from django.contrib import admin

from apps.triaje.models import EvaluacionTriaje, SolicitudAtencion


@admin.register(SolicitudAtencion)
class SolicitudAtencionAdmin(admin.ModelAdmin):
    list_display = ("codigo", "paciente", "motivo", "estado", "creado_en")
    list_filter = ("estado",)
    search_fields = ("codigo", "motivo", "paciente__nombres", "paciente__apellidos")
    autocomplete_fields = ("paciente",)


@admin.register(EvaluacionTriaje)
class EvaluacionTriajeAdmin(admin.ModelAdmin):
    list_display = ("solicitud", "nivel_urgencia", "evaluado_por", "creado_en")
    list_filter = ("nivel_urgencia",)
    search_fields = ("solicitud__codigo",)
