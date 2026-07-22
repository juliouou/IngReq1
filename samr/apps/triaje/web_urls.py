"""Rutas web de la app triaje."""
from django.urls import path

from apps.triaje import web_views as views

app_name = "triaje"

urlpatterns = [
    path("", views.solicitudes_lista, name="lista"),
    path("nueva/", views.nueva_solicitud, name="nueva"),
    path("<int:solicitud_id>/", views.detalle_solicitud, name="detalle"),
]
