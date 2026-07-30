"""Rutas de la app auditoria."""
from rest_framework.routers import DefaultRouter

from apps.auditoria.views import RegistroAuditoriaViewSet

router = DefaultRouter()
router.register("registros", RegistroAuditoriaViewSet, basename="registro-auditoria")

urlpatterns = router.urls
