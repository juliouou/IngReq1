"""Context processors de la app teleconsulta."""
from apps.teleconsulta.models import Receta


def notificaciones_teleconsulta(request):
    """Agrega tiene_recetas_nuevas al contexto de todas las plantillas."""
    if request.user.is_authenticated and request.user.rol == "PACIENTE":
        recetas_nuevas = Receta.objects.filter(
            teleconsulta__paciente=request.user, leida=False
        ).exists()
        return {"tiene_recetas_nuevas": recetas_nuevas}
    return {"tiene_recetas_nuevas": False}
