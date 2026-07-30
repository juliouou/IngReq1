"""Validadores especificos de la app usuarios."""
from django.core.exceptions import ValidationError

from shared.constants import Roles


def validar_rol(rol):
    """Valida que el rol pertenezca a los roles soportados."""
    if rol not in Roles.TODOS:
        raise ValidationError("El rol '{0}' no es valido.".format(rol))
    return rol
