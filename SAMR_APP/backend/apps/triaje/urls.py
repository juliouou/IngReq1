"""Rutas de la app triaje."""
from rest_framework.routers import DefaultRouter

from apps.triaje.views import SolicitudAtencionViewSet

router = DefaultRouter()
router.register("solicitudes", SolicitudAtencionViewSet, basename="solicitud")

urlpatterns = router.urls
