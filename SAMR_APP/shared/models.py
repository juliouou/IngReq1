"""Modelos abstractos base reutilizables por las apps del proyecto."""
from django.db import models


class ModeloBase(models.Model):
    """
    Modelo abstracto con marcas de tiempo de creacion y actualizacion.

    Al ser abstracto no genera tabla propia; las apps concretas lo heredan.
    """

    creado_en = models.DateTimeField("Creado en", auto_now_add=True)
    actualizado_en = models.DateTimeField("Actualizado en", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-creado_en"]
