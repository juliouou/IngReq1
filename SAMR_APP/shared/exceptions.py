"""Excepciones personalizadas y manejador de excepciones para DRF."""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("samr")


class SamrException(Exception):
    """Excepcion base del dominio SAMR."""

    default_message = "Error en el sistema SAMR."
    default_code = "error_samr"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, code=None, status_code=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)


class ReglaNegocioError(SamrException):
    """Se viola una regla de negocio."""

    default_message = "La operacion viola una regla de negocio."
    default_code = "regla_negocio"
    status_code = status.HTTP_400_BAD_REQUEST


class RecursoNoEncontrado(SamrException):
    """El recurso solicitado no existe."""

    default_message = "El recurso solicitado no existe."
    default_code = "no_encontrado"
    status_code = status.HTTP_404_NOT_FOUND


class OperacionNoPermitida(SamrException):
    """El usuario no tiene permisos para la operacion."""

    default_message = "No tiene permisos para realizar esta accion."
    default_code = "no_permitido"
    status_code = status.HTTP_403_FORBIDDEN


class ConflictoEstado(SamrException):
    """El recurso esta en un estado que impide la operacion."""

    default_message = "El recurso esta en un estado que impide la operacion."
    default_code = "conflicto_estado"
    status_code = status.HTTP_409_CONFLICT


def _extraer_mensaje(detalle):
    """Obtiene un mensaje legible a partir del cuerpo de error de DRF."""
    if isinstance(detalle, dict):
        if "detail" in detalle:
            return str(detalle["detail"])
        for valor in detalle.values():
            if isinstance(valor, (list, tuple)) and valor:
                return str(valor[0])
            return str(valor)
    if isinstance(detalle, (list, tuple)) and detalle:
        return str(detalle[0])
    return str(detalle)


def custom_exception_handler(exc, context):
    """
    Manejador de excepciones unificado.

    Normaliza tanto las excepciones del dominio (SamrException) como las de
    DRF hacia una estructura consistente:
        {"exito": False, "mensaje": ..., "codigo": ..., "errores": ...}
    """
    if isinstance(exc, SamrException):
        logger.warning("SamrException [%s]: %s", exc.code, exc.message)
        return Response(
            {
                "exito": False,
                "mensaje": exc.message,
                "codigo": exc.code,
                "errores": None,
            },
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        detalle = response.data
        response.data = {
            "exito": False,
            "mensaje": _extraer_mensaje(detalle),
            "codigo": "error_validacion",
            "errores": detalle,
        }
        return response

    logger.exception("Error no controlado en la peticion")
    return Response(
        {
            "exito": False,
            "mensaje": "Error interno del servidor.",
            "codigo": "error_interno",
            "errores": None,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
