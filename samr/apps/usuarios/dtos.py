"""DTOs de la app usuarios."""
from dataclasses import dataclass
from typing import Optional

from core.dtos import BaseDTO


@dataclass
class UsuarioDTO(BaseDTO):
    email: str
    nombres: str
    apellidos: str
    rol: str
    cedula: Optional[str] = None
    telefono: str = ""
