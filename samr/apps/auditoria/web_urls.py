"""Rutas web de la app auditoria."""
from django.urls import path

from apps.auditoria import web_views as views

app_name = "auditoria"

urlpatterns = [
    path("", views.panel_auditoria, name="panel"),
]
