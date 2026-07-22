"""Repositorio base (Repository Pattern) reutilizable por las apps."""


class BaseRepository:
    """
    Encapsula el acceso a datos de un modelo concreto.

    Las apps definen repositorios que heredan de esta clase y fijan `model`.
    """

    model = None

    def __init__(self, model=None):
        if model is not None:
            self.model = model
        if self.model is None:
            raise ValueError("El repositorio requiere un modelo definido.")

    def get_queryset(self):
        return self.model.objects.all()

    def listar(self, **filtros):
        return self.get_queryset().filter(**filtros)

    def obtener_por_id(self, identificador):
        return self.get_queryset().filter(pk=identificador).first()

    def obtener_por(self, **filtros):
        return self.get_queryset().filter(**filtros).first()

    def crear(self, **datos):
        return self.model.objects.create(**datos)

    def actualizar(self, instancia, **datos):
        for campo, valor in datos.items():
            setattr(instancia, campo, valor)
        instancia.save()
        return instancia

    def eliminar(self, instancia):
        instancia.delete()

    def existe(self, **filtros):
        return self.get_queryset().filter(**filtros).exists()

    def contar(self, **filtros):
        return self.get_queryset().filter(**filtros).count()
