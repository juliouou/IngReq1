"""Rutas de la app teleconsulta."""
from rest_framework.routers import DefaultRouter

from apps.teleconsulta.views import (
    HistorialClinicoViewSet,
    TeleconsultaViewSet,
)

router = DefaultRouter()
router.register("teleconsultas", TeleconsultaViewSet, basename="teleconsulta")
router.register("historial", HistorialClinicoViewSet, basename="historial")

urlpatterns = router.urls
