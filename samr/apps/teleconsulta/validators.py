"""Validadores de la app teleconsulta."""
from django.core.exceptions import ValidationError


def validar_medicamentos(medicamentos):
    """Valida la estructura de la lista de medicamentos de una receta."""
    if not isinstance(medicamentos, list) or not medicamentos:
        raise ValidationError("Debe indicar al menos un medicamento.")
    requeridos = {"medicamento", "dosis", "frecuencia", "duracion"}
    for item in medicamentos:
        if not isinstance(item, dict) or not requeridos.issubset(item.keys()):
            raise ValidationError(
                "Cada medicamento requiere: medicamento, dosis, frecuencia y duracion."
            )
    return medicamentos
