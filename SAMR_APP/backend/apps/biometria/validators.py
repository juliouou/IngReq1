"""Validadores de la app biometria."""
from django.core.exceptions import ValidationError

from apps.biometria.models import TipoSigno


def validar_tipo_signo(tipo_signo):
    """Valida que el tipo de signo pertenezca a los soportados."""
    validos = [valor for valor, _ in TipoSigno.CHOICES]
    if tipo_signo not in validos:
        raise ValidationError("El tipo de signo '{0}' no es valido.".format(tipo_signo))
    return tipo_signo
