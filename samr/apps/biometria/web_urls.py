"""Rutas web de la app biometria."""
from django.urls import path

from apps.biometria import web_views as views

app_name = "biometria"

urlpatterns = [
    path("", views.dashboard_biometrico, name="dashboard"),
    path("alertas/<int:alerta_id>/atender/", views.atender_alerta, name="atender_alerta"),
]
