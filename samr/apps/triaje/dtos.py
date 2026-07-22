"""DTOs de la app triaje."""
from dataclasses import dataclass

from core.dtos import BaseDTO


@dataclass
class SolicitudDTO(BaseDTO):
    codigo: str
    paciente_id: int
    motivo: str
    sintomas: str
    estado: str
