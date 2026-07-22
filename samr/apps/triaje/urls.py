"""Rutas de la app triaje."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.triaje.views import SolicitudAtencionViewSet, AnalizarSintomasView

router = DefaultRouter()
router.register("solicitudes", SolicitudAtencionViewSet, basename="solicitud")

urlpatterns = [
    path('analizar-sintomas/', AnalizarSintomasView.as_view(), name='analizar-sintomas'),
] + router.urls
