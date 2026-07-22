"""DTOs base (Data Transfer Objects) del proyecto SAMR."""
from dataclasses import asdict, dataclass, fields


@dataclass
class BaseDTO:
    """DTO base con utilidades de conversion desde/hacia diccionarios."""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        nombres = {campo.name for campo in fields(cls)}
        filtrado = {clave: valor for clave, valor in data.items() if clave in nombres}
        return cls(**filtrado)
