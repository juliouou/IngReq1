"""Rutas de la app biometria."""
from rest_framework.routers import DefaultRouter

from apps.biometria.views import (
    AlertaViewSet,
    DispositivoIoTViewSet,
    LecturaBiometricaViewSet,
)

router = DefaultRouter()
router.register("dispositivos", DispositivoIoTViewSet, basename="dispositivo")
router.register("lecturas", LecturaBiometricaViewSet, basename="lectura")
router.register("alertas", AlertaViewSet, basename="alerta")

urlpatterns = router.urls
