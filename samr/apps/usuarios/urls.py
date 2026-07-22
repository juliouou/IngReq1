"""Rutas de la app usuarios."""
from rest_framework.routers import DefaultRouter

from apps.usuarios.views import (
    PerfilMedicoViewSet,
    PerfilPacienteViewSet,
    UsuarioViewSet,
)

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuario")
router.register("perfiles-medicos", PerfilMedicoViewSet, basename="perfil-medico")
router.register("perfiles-pacientes", PerfilPacienteViewSet, basename="perfil-paciente")

urlpatterns = router.urls
