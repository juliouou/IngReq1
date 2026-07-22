"""Servicios de la app biometria (Service Layer)."""
from django.db import transaction

from core.services import BaseService
from core.utils import generar_codigo
from apps.biometria.models import (
    Alerta,
    DispositivoIoT,
    LecturaBiometrica,
    NivelAlerta,
    TipoSigno,
)
from apps.biometria.repositories import DispositivoRepository, LecturaRepository


class DispositivoService(BaseService):
    repository_class = DispositivoRepository

    @transaction.atomic
    def registrar_dispositivo(self, paciente, nombre, tipo, numero_serie):
        return self.repository.crear(
            codigo=generar_codigo("DEV-", 8),
            nombre=nombre,
            tipo=tipo,
            paciente=paciente,
            numero_serie=numero_serie,
        )


class LecturaService(BaseService):
    repository_class = LecturaRepository

    @transaction.atomic
    def registrar_lectura(self, dispositivo, tipo_signo, valor, unidad=""):
        """
        Registra una lectura y marca si esta fuera de rango.

        La generacion de alerta y su emision por WebSocket se delega al signal
        post_save de LecturaBiometrica (ver signals.py), evitando duplicar la
        logica de notificacion.
        """
        lectura = LecturaBiometrica(
            dispositivo=dispositivo,
            tipo_signo=tipo_signo,
            valor=valor,
            unidad=unidad,
        )
        lectura.fuera_de_rango = lectura.evaluar_rango()
        lectura.save()
        return lectura

    @staticmethod
    def clasificar_nivel(tipo_signo, valor):
        """Clasifica la severidad de una lectura fuera de rango."""
        rango = TipoSigno.RANGOS.get(tipo_signo)
        if not rango:
            return NivelAlerta.INFO
        minimo, maximo = rango
        valor = float(valor)
        # Desviacion relativa respecto al limite superado.
        if valor < minimo:
            desviacion = (minimo - valor) / max(minimo, 1)
        else:
            desviacion = (valor - maximo) / max(maximo, 1)
        if desviacion >= 0.20:
            return NivelAlerta.CRITICA
        if desviacion >= 0.05:
            return NivelAlerta.ADVERTENCIA
        return NivelAlerta.INFO


def generar_alerta_desde_lectura(lectura):
    """
    Crea una alerta a partir de una lectura fuera de rango.

    Se define a nivel de modulo para poder reutilizarla desde el signal.
    Devuelve la alerta creada o None si la lectura esta dentro de rango.
    """
    if not lectura.fuera_de_rango:
        return None

    nivel = LecturaService.clasificar_nivel(lectura.tipo_signo, lectura.valor)
    etiqueta = dict(TipoSigno.CHOICES).get(lectura.tipo_signo, lectura.tipo_signo)
    mensaje = "{0}: valor {1} fuera de rango.".format(etiqueta, lectura.valor)

    return Alerta.objects.create(
        lectura=lectura,
        paciente=lectura.dispositivo.paciente,
        nivel=nivel,
        mensaje=mensaje,
    )
