"""Rutas web de la app teleconsulta."""
from django.urls import path

from apps.teleconsulta import web_views as views

app_name = "teleconsulta"

urlpatterns = [
    path("", views.lista_teleconsultas, name="lista"),
    path("<int:teleconsulta_id>/", views.detalle_teleconsulta, name="detalle"),
]
