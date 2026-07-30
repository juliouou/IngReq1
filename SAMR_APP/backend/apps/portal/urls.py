"""Rutas de la app portal."""
from django.urls import path

from apps.portal import views

app_name = "portal"

urlpatterns = [
    path("", views.login_view, name="inicio"),
    path("registro/", views.registro_view, name="registro"),
    path("login/", views.login_view, name="login"),
    path("verificar-mfa/", views.verificar_mfa_view, name="verificar_mfa"),
    path("reenviar-mfa/", views.reenviar_mfa_view, name="reenviar_mfa"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
]
