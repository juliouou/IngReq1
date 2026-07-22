"""DTOs de la app biometria."""
from dataclasses import dataclass

from core.dtos import BaseDTO


@dataclass
class LecturaDTO(BaseDTO):
    dispositivo_id: int
    tipo_signo: str
    valor: float
    unidad: str = ""
