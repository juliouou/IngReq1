"""Repositorios de la app biometria."""
from core.repositories import BaseRepository
from apps.biometria.models import Alerta, DispositivoIoT, LecturaBiometrica


class DispositivoRepository(BaseRepository):
    model = DispositivoIoT

    def listar_activos(self):
        return self.get_queryset().filter(activo=True)

    def listar_por_paciente(self, paciente_id):
        return self.get_queryset().filter(paciente_id=paciente_id)


class LecturaRepository(BaseRepository):
    model = LecturaBiometrica

    def listar_por_dispositivo(self, dispositivo_id):
        return self.get_queryset().filter(dispositivo_id=dispositivo_id)

    def listar_fuera_de_rango(self):
        return self.get_queryset().filter(fuera_de_rango=True)


class AlertaRepository(BaseRepository):
    model = Alerta

    def listar_pendientes(self):
        return self.get_queryset().filter(atendida=False)
