"""DTOs de la app teleconsulta."""
from dataclasses import dataclass, field
from typing import List

from shared.dtos import BaseDTO


@dataclass
class MedicamentoDTO(BaseDTO):
    medicamento: str
    dosis: str
    frecuencia: str
    duracion: str


@dataclass
class RecetaDTO(BaseDTO):
    teleconsulta_id: int
    indicaciones_generales: str = ""
    medicamentos: List[dict] = field(default_factory=list)
