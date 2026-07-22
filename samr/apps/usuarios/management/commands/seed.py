"""
Comando de siembra de datos de prueba para el sistema SAMR.

Genera de forma relacionada y sin datos quemados en los modelos:
administrador, medicos, pacientes, solicitudes de atencion, evaluaciones
de triaje, teleconsultas, recetas, dispositivos IoT, lecturas biometricas,
alertas (via signal) e historial clinico (via service).

Uso:
    python manage.py seed
    python manage.py seed --medicos 5 --pacientes 12
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.constants import Roles
from core.utils import (
    generar_cedula_valida,
    generar_codigo,
    generar_telefono_ec,
)
from apps.usuarios.models import PerfilMedico, PerfilPaciente, Usuario
from apps.triaje.models import NivelUrgencia
from apps.triaje.services import SolicitudService
from apps.biometria.models import TipoDispositivo, TipoSigno
from apps.biometria.services import DispositivoService, LecturaService
from apps.teleconsulta.services import RecetaService, TeleconsultaService
from apps.auditoria.services import RegistroAuditoriaService


# Pools para generacion aleatoria (no son datos quemados en el modelo:
# son fuentes de variacion para el seeder, como haria una libreria faker).
NOMBRES = [
    "Maria", "Jose", "Ana", "Luis", "Carmen", "Jorge", "Elena", "Diego",
    "Sofia", "Andres", "Paula", "Kevin", "Daniela", "Bryan", "Gabriela", "Marco",
]
APELLIDOS = [
    "Gonzalez", "Ramirez", "Torres", "Flores", "Vega", "Cardenas", "Loayza",
    "Jimenez", "Castillo", "Paredes", "Robalino", "Condoy", "Lopez", "Parra",
]
ESPECIALIDADES = [
    "Medicina General", "Cardiologia", "Pediatria", "Dermatologia",
    "Neurologia", "Ginecologia", "Traumatologia",
]
MOTIVOS = [
    "Dolor de cabeza persistente", "Fiebre alta", "Control de presion arterial",
    "Dificultad para respirar", "Dolor abdominal", "Control de glucosa",
    "Malestar general", "Mareos frecuentes",
]
SINTOMAS = [
    "El paciente refiere molestias desde hace varios dias.",
    "Sintomas intermitentes que empeoran por la noche.",
    "Cuadro acompanado de cansancio y falta de apetito.",
    "Dolor localizado sin irradiacion aparente.",
    "Episodios recurrentes durante la ultima semana.",
]
ALERGIAS = ["Ninguna conocida", "Penicilina", "Polen", "Mariscos", "Aspirina"]
ANTECEDENTES = [
    "Sin antecedentes relevantes.",
    "Hipertension controlada.",
    "Diabetes tipo 2.",
    "Asma leve.",
    "Antecedente quirurgico de apendicectomia.",
]
TIPOS_SANGRE = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
DIAGNOSTICOS = [
    "Cuadro viral autolimitado.",
    "Hipertension arterial en seguimiento.",
    "Gastritis aguda.",
    "Infeccion respiratoria alta.",
    "Control metabolico dentro de parametros.",
]
MEDICAMENTOS = [
    {"medicamento": "Paracetamol 500mg", "dosis": "1 tableta",
     "frecuencia": "Cada 8 horas", "duracion": "5 dias"},
    {"medicamento": "Ibuprofeno 400mg", "dosis": "1 tableta",
     "frecuencia": "Cada 12 horas", "duracion": "3 dias"},
    {"medicamento": "Amoxicilina 500mg", "dosis": "1 capsula",
     "frecuencia": "Cada 8 horas", "duracion": "7 dias"},
    {"medicamento": "Losartan 50mg", "dosis": "1 tableta",
     "frecuencia": "Cada 24 horas", "duracion": "30 dias"},
    {"medicamento": "Omeprazol 20mg", "dosis": "1 capsula",
     "frecuencia": "En ayunas", "duracion": "14 dias"},
]

# Mapa tipo de dispositivo -> (tipo de signo, unidad) que reporta.
SIGNO_POR_DISPOSITIVO = {
    TipoDispositivo.PULSERA: (TipoSigno.FRECUENCIA_CARDIACA, "lpm"),
    TipoDispositivo.OXIMETRO: (TipoSigno.SATURACION_OXIGENO, "%"),
    TipoDispositivo.TENSIOMETRO: (TipoSigno.PRESION_SISTOLICA, "mmHg"),
    TipoDispositivo.TERMOMETRO: (TipoSigno.TEMPERATURA, "C"),
    TipoDispositivo.GLUCOMETRO: (TipoSigno.GLUCOSA, "mg/dL"),
}

PASSWORD_DEMO = "Samr2026*"
DOMINIO = "@samr.local"


class Command(BaseCommand):
    help = "Genera datos de prueba relacionados para el sistema SAMR."

    def add_arguments(self, parser):
        parser.add_argument("--medicos", type=int, default=4,
                            help="Cantidad de medicos a generar.")
        parser.add_argument("--pacientes", type=int, default=8,
                            help="Cantidad de pacientes a generar.")

    def handle(self, *args, **options):
        num_medicos = max(1, options["medicos"])
        num_pacientes = max(1, options["pacientes"])

        self.stdout.write(self.style.WARNING("Iniciando siembra de datos SAMR..."))

        with transaction.atomic():
            self._limpiar()
            admin = self._crear_admin()
            medicos = self._crear_medicos(num_medicos)
            pacientes = self._crear_pacientes(num_pacientes)
            solicitudes = self._crear_solicitudes(pacientes, medicos)
            self._crear_teleconsultas(solicitudes, medicos)
            self._crear_biometria(pacientes)
            self._crear_auditoria(admin)

        self.stdout.write(self.style.SUCCESS("Siembra completada correctamente."))
        self.stdout.write("")
        self.stdout.write("Credenciales de acceso (todas con la misma clave):")
        self.stdout.write("  Clave: {0}".format(PASSWORD_DEMO))
        self.stdout.write("  Admin: admin{0}".format(DOMINIO))
        self.stdout.write(
            "  Medicos: medico1{0} ... medico{1}{0}".format(DOMINIO, num_medicos)
        )
        self.stdout.write(
            "  Pacientes: paciente1{0} ... paciente{1}{0}".format(
                DOMINIO, num_pacientes
            )
        )

    # ------------------------------------------------------------------ #
    # Utilidades internas
    # ------------------------------------------------------------------ #

    def _limpiar(self):
        """Elimina unicamente los usuarios sembrados (y en cascada sus datos)."""
        borrados, _ = Usuario.objects.filter(email__endswith=DOMINIO).delete()
        self.stdout.write("  - Datos previos de siembra eliminados: {0}".format(borrados))

    def _cedula_unica(self, usadas):
        cedula = generar_cedula_valida()
        while cedula in usadas:
            cedula = generar_cedula_valida()
        usadas.add(cedula)
        return cedula

    # ------------------------------------------------------------------ #
    # Creacion de usuarios
    # ------------------------------------------------------------------ #

    def _crear_admin(self):
        admin = Usuario.objects.create_superuser(
            email="admin{0}".format(DOMINIO),
            password=PASSWORD_DEMO,
            nombres="Administrador",
            apellidos="SAMR",
        )
        self.stdout.write(self.style.SUCCESS("  - Administrador creado."))
        return admin

    def _crear_medicos(self, cantidad):
        medicos = []
        usadas = set()
        for indice in range(1, cantidad + 1):
            usuario = Usuario.objects.create_user(
                email="medico{0}{1}".format(indice, DOMINIO),
                password=PASSWORD_DEMO,
                nombres=random.choice(NOMBRES),
                apellidos=random.choice(APELLIDOS),
                rol=Roles.MEDICO,
                cedula=self._cedula_unica(usadas),
                telefono=generar_telefono_ec(),
            )
            # El signal ya creo el PerfilMedico; aqui se completan sus datos.
            perfil = PerfilMedico.objects.get(usuario=usuario)
            perfil.especialidad = random.choice(ESPECIALIDADES)
            perfil.numero_registro = "MED-{0:04d}".format(indice)
            perfil.anios_experiencia = random.randint(1, 25)
            perfil.disponible = True
            perfil.save()
            medicos.append(usuario)
        self.stdout.write(self.style.SUCCESS(
            "  - {0} medicos creados.".format(len(medicos))
        ))
        return medicos

    def _crear_pacientes(self, cantidad):
        pacientes = []
        usadas = set()
        hoy = timezone.now().date()
        for indice in range(1, cantidad + 1):
            usuario = Usuario.objects.create_user(
                email="paciente{0}{1}".format(indice, DOMINIO),
                password=PASSWORD_DEMO,
                nombres=random.choice(NOMBRES),
                apellidos=random.choice(APELLIDOS),
                rol=Roles.PACIENTE,
                cedula=self._cedula_unica(usadas),
                telefono=generar_telefono_ec(),
            )
            # El signal ya creo el PerfilPaciente; aqui se completan sus datos.
            perfil = PerfilPaciente.objects.get(usuario=usuario)
            perfil.fecha_nacimiento = hoy - timedelta(
                days=random.randint(18 * 365, 80 * 365)
            )
            perfil.tipo_sangre = random.choice(TIPOS_SANGRE)
            perfil.alergias = random.choice(ALERGIAS)
            perfil.antecedentes = random.choice(ANTECEDENTES)
            perfil.save()
            pacientes.append(usuario)
        self.stdout.write(self.style.SUCCESS(
            "  - {0} pacientes creados.".format(len(pacientes))
        ))
        return pacientes

    # ------------------------------------------------------------------ #
    # Creacion del dominio clinico
    # ------------------------------------------------------------------ #

    def _crear_solicitudes(self, pacientes, medicos):
        service = SolicitudService()
        solicitudes = []
        for paciente in pacientes:
            for _ in range(random.randint(1, 2)):
                solicitud = service.crear_solicitud(
                    paciente=paciente,
                    motivo=random.choice(MOTIVOS),
                    sintomas=random.choice(SINTOMAS),
                )
                # A una parte de las solicitudes se les registra triaje.
                if random.random() < 0.7:
                    service.registrar_triaje(
                        solicitud=solicitud,
                        evaluado_por=random.choice(medicos),
                        nivel_urgencia=random.randint(
                            NivelUrgencia.EMERGENCIA, NivelUrgencia.NO_URGENTE
                        ),
                        observaciones="Evaluacion inicial de triaje.",
                        temperatura=Decimal(
                            str(round(random.uniform(36.0, 39.0), 1))
                        ),
                        frecuencia_cardiaca=random.randint(55, 120),
                    )
                solicitudes.append(solicitud)
        self.stdout.write(self.style.SUCCESS(
            "  - {0} solicitudes de atencion creadas.".format(len(solicitudes))
        ))
        return solicitudes

    def _crear_teleconsultas(self, solicitudes, medicos):
        service = TeleconsultaService()
        receta_service = RecetaService()
        total_tc = 0
        total_recetas = 0
        ahora = timezone.now()

        for solicitud in solicitudes:
            if random.random() < 0.6:
                continue  # no todas las solicitudes derivan en teleconsulta

            medico = random.choice(medicos)
            teleconsulta = service.agendar(
                medico=medico,
                paciente=solicitud.paciente,
                fecha_programada=ahora + timedelta(days=random.randint(1, 15)),
                motivo=solicitud.motivo,
                solicitud=solicitud,
            )
            total_tc += 1

            # Una parte se lleva hasta finalizada (genera historial clinico).
            if random.random() < 0.7:
                service.iniciar(teleconsulta)
                service.finalizar(
                    teleconsulta,
                    diagnostico=random.choice(DIAGNOSTICOS),
                    notas="Se brindan indicaciones y seguimiento al paciente.",
                )
                # A las finalizadas se les emite receta.
                if random.random() < 0.8:
                    cantidad = random.randint(1, 3)
                    seleccion = random.sample(
                        MEDICAMENTOS, k=min(cantidad, len(MEDICAMENTOS))
                    )
                    receta_service.emitir(
                        teleconsulta=teleconsulta,
                        indicaciones_generales="Reposo relativo e hidratacion.",
                        medicamentos=[dict(item) for item in seleccion],
                    )
                    total_recetas += 1

        self.stdout.write(self.style.SUCCESS(
            "  - {0} teleconsultas y {1} recetas creadas.".format(
                total_tc, total_recetas
            )
        ))

    def _crear_biometria(self, pacientes):
        disp_service = DispositivoService()
        lectura_service = LecturaService()
        tipos = [tipo for tipo, _ in TipoDispositivo.CHOICES]
        total_disp = 0
        total_lecturas = 0

        for paciente in pacientes:
            for _ in range(random.randint(1, 2)):
                tipo = random.choice(tipos)
                dispositivo = disp_service.registrar_dispositivo(
                    paciente=paciente,
                    nombre="{0} de {1}".format(
                        tipo.capitalize(), paciente.nombres
                    ),
                    tipo=tipo,
                    numero_serie=generar_codigo("SN-", 10),
                )
                total_disp += 1

                tipo_signo, unidad = SIGNO_POR_DISPOSITIVO[tipo]
                minimo, maximo = TipoSigno.RANGOS[tipo_signo]

                for _ in range(random.randint(3, 6)):
                    if random.random() < 0.35:
                        # Valor fuera de rango: dispara alerta via signal.
                        if random.random() < 0.5:
                            valor = round(minimo * random.uniform(0.5, 0.85), 2)
                        else:
                            valor = round(maximo * random.uniform(1.15, 1.5), 2)
                    else:
                        valor = round(random.uniform(minimo, maximo), 2)

                    lectura_service.registrar_lectura(
                        dispositivo=dispositivo,
                        tipo_signo=tipo_signo,
                        valor=Decimal(str(valor)),
                        unidad=unidad,
                    )
                    total_lecturas += 1

        self.stdout.write(self.style.SUCCESS(
            "  - {0} dispositivos y {1} lecturas creadas "
            "(las alertas se generan automaticamente).".format(
                total_disp, total_lecturas
            )
        ))

    def _crear_auditoria(self, admin):
        """Crea algunos registros de auditoria de ejemplo (endpoint no vacio)."""
        service = RegistroAuditoriaService()
        rutas = [
            ("POST", "/api/usuarios/usuarios/", 201),
            ("POST", "/api/triaje/solicitudes/", 201),
            ("POST", "/api/teleconsulta/teleconsultas/agendar/", 201),
            ("PATCH", "/api/biometria/alertas/1/atender/", 200),
        ]
        for accion, ruta, codigo in rutas:
            service.registrar(
                usuario=admin,
                accion=accion,
                ruta=ruta,
                codigo_estado=codigo,
                request_id=generar_codigo("", 32).lower(),
                ip="127.0.0.1",
            )
        self.stdout.write(self.style.SUCCESS(
            "  - {0} registros de auditoria creados.".format(len(rutas))
        ))
