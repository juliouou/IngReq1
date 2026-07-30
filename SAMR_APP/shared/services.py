"""Servicio base (Service Layer) reutilizable por las apps."""
from shared.exceptions import RecursoNoEncontrado


class BaseService:
    """
    Orquesta la logica de negocio apoyandose en un repositorio.

    Las apps definen servicios que heredan de esta clase y fijan
    `repository_class`.
    """

    repository_class = None

    def __init__(self, repository=None):
        if repository is not None:
            self.repository = repository
        elif self.repository_class is not None:
            self.repository = self.repository_class()
        else:
            raise ValueError("El servicio requiere un repositorio.")

    def listar(self, **filtros):
        return self.repository.listar(**filtros)

    def obtener(self, identificador):
        instancia = self.repository.obtener_por_id(identificador)
        if instancia is None:
            raise RecursoNoEncontrado()
        return instancia

    def crear(self, **datos):
        return self.repository.crear(**datos)

    def actualizar(self, identificador, **datos):
        instancia = self.obtener(identificador)
        return self.repository.actualizar(instancia, **datos)

    def eliminar(self, identificador):
        instancia = self.obtener(identificador)
        self.repository.eliminar(instancia)
