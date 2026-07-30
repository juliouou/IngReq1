"""Admin de la app teleconsulta."""
from django.contrib import admin

from apps.teleconsulta.models import (
    DetalleReceta,
    HistorialClinico,
    Receta,
    Teleconsulta,
)


class DetalleRecetaInline(admin.TabularInline):
    model = DetalleReceta
    extra = 0


@admin.register(Teleconsulta)
class TeleconsultaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "medico", "paciente", "estado", "fecha_programada")
    list_filter = ("estado",)
    search_fields = ("codigo", "motivo")
    autocomplete_fields = ("medico", "paciente")


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "teleconsulta", "creado_en")
    search_fields = ("codigo",)
    inlines = [DetalleRecetaInline]


@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ("paciente", "teleconsulta", "creado_en")
    search_fields = ("paciente__nombres", "paciente__apellidos")
