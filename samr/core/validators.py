"""Validadores reutilizables del dominio SAMR."""
import re

from django.core.exceptions import ValidationError

_TELEFONO_RE = re.compile(r"^\+?\d{7,15}$")


def validar_cedula_ecuatoriana(cedula):
    """
    Valida una cedula ecuatoriana de 10 digitos usando el digito verificador.

    Lanza ValidationError si la cedula no es valida.
    """
    if not isinstance(cedula, str) or not cedula.isdigit() or len(cedula) != 10:
        raise ValidationError("La cedula debe tener 10 digitos numericos.")

    provincia = int(cedula[0:2])
    if provincia < 1 or (provincia > 24 and provincia != 30):
        raise ValidationError("El codigo de provincia de la cedula es invalido.")

    tercer_digito = int(cedula[2])
    if tercer_digito >= 6:
        raise ValidationError("El tercer digito de la cedula es invalido.")

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for indice in range(9):
        producto = int(cedula[indice]) * coeficientes[indice]
        if producto >= 10:
            producto -= 9
        total += producto

    verificador = (10 - (total % 10)) % 10
    if verificador != int(cedula[9]):
        raise ValidationError("La cedula no es valida (digito verificador).")

    return cedula


def validar_telefono(telefono):
    """Valida un numero de telefono (7 a 15 digitos, con prefijo + opcional)."""
    if not isinstance(telefono, str) or not _TELEFONO_RE.match(telefono):
        raise ValidationError("El telefono debe tener entre 7 y 15 digitos.")
    return telefono


def validar_positivo(valor):
    """Valida que un valor numerico sea estrictamente positivo."""
    if valor is None or valor <= 0:
        raise ValidationError("El valor debe ser mayor que cero.")
    return valor
