"""Validadores de la app triaje."""
from django.core.exceptions import ValidationError

from apps.triaje.models import NivelUrgencia


def validar_nivel_urgencia(nivel):
    """Valida que el nivel de urgencia sea uno de los definidos."""
    validos = [valor for valor, _ in NivelUrgencia.CHOICES]
    if nivel not in validos:
        raise ValidationError("El nivel de urgencia no es valido.")
    return nivel
