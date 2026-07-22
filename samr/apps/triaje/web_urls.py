"""Rutas web de la app triaje."""
from django.urls import path

from apps.triaje import web_views as views

app_name = "triaje"

urlpatterns = [
    path("", views.solicitudes_lista, name="lista"),
    path("chat/", views.chat_triaje, name="chat"),
    path("chat/nuevo/", views.chat_nuevo, name="chat_nuevo"),
    path("chat/<int:solicitud_id>/", views.chat_ver, name="chat_ver"),
    path("<int:solicitud_id>/", views.detalle_solicitud, name="detalle"),
    path("<int:solicitud_id>/escalar/", views.escalar_a_humano, name="escalar"),
]
