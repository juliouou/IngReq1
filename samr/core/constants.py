"""Constantes compartidas por todo el proyecto SAMR."""


class Roles:
    """Roles de usuario del sistema."""

    ADMIN = "ADMIN"
    MEDICO = "MEDICO"
    PACIENTE = "PACIENTE"

    CHOICES = (
        (ADMIN, "Administrador"),
        (MEDICO, "Medico"),
        (PACIENTE, "Paciente"),
    )

    TODOS = (ADMIN, MEDICO, PACIENTE)


class MensajesError:
    """Mensajes de error reutilizables."""

    NO_ENCONTRADO = "El recurso solicitado no existe."
    NO_PERMITIDO = "No tiene permisos para realizar esta accion."
    REGLA_NEGOCIO = "La operacion viola una regla de negocio."
    CONFLICTO = "El recurso se encuentra en un estado que impide la operacion."
