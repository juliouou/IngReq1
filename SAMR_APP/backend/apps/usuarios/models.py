"""Modelos de la app usuarios: usuario personalizado y perfiles."""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from shared.constants import Roles
from shared.models import ModeloBase
from apps.usuarios.managers import UsuarioManager


class TipoSangre:
    """Opciones de tipo de sangre."""

    CHOICES = (
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    )


class Usuario(AbstractBaseUser, PermissionsMixin, ModeloBase):
    """Usuario personalizado del sistema (login por email)."""

    email = models.EmailField("Correo electronico", unique=True)
    nombres = models.CharField("Nombres", max_length=120)
    apellidos = models.CharField("Apellidos", max_length=120)
    cedula = models.CharField(
        "Cedula", max_length=10, unique=True, null=True, blank=True
    )
    telefono = models.CharField("Telefono", max_length=15, blank=True)
    afiliacion_iess = models.CharField(
        "Afiliacion IESS", max_length=50, blank=True,
        help_text="Numero de afiliacion validado contra el IESS/MSP (RF-02).",
    )
    rol = models.CharField(
        "Rol", max_length=20, choices=Roles.CHOICES, default=Roles.PACIENTE
    )
    is_active = models.BooleanField("Activo", default=True)
    is_staff = models.BooleanField("Es staff", default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombres", "apellidos"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-creado_en"]

    def __str__(self):
        return "{0} {1} ({2})".format(self.nombres, self.apellidos, self.email)

    @property
    def nombre_completo(self):
        return "{0} {1}".format(self.nombres, self.apellidos).strip()

    @property
    def es_admin(self):
        return self.is_superuser or self.rol == Roles.ADMIN

    @property
    def es_medico(self):
        return self.rol == Roles.MEDICO

    @property
    def es_paciente(self):
        return self.rol == Roles.PACIENTE


class PerfilMedico(ModeloBase):
    """Informacion profesional asociada a un usuario con rol MEDICO."""

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="perfil_medico"
    )
    especialidad = models.CharField("Especialidad", max_length=120)
    numero_registro = models.CharField(
        "Numero de registro", max_length=40, unique=True
    )
    anios_experiencia = models.PositiveIntegerField("Anios de experiencia", default=0)
    disponible = models.BooleanField("Disponible", default=True)

    class Meta:
        verbose_name = "Perfil de medico"
        verbose_name_plural = "Perfiles de medicos"
        ordering = ["-creado_en"]

    def __str__(self):
        return "Dr(a). {0} - {1}".format(
            self.usuario.nombre_completo, self.especialidad
        )


class PerfilPaciente(ModeloBase):
    """Informacion clinica basica asociada a un usuario con rol PACIENTE."""

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="perfil_paciente"
    )
    fecha_nacimiento = models.DateField("Fecha de nacimiento", null=True, blank=True)
    tipo_sangre = models.CharField(
        "Tipo de sangre", max_length=3, choices=TipoSangre.CHOICES, blank=True
    )
    alergias = models.TextField("Alergias", blank=True)
    antecedentes = models.TextField("Antecedentes medicos", blank=True)

    class Meta:
        verbose_name = "Perfil de paciente"
        verbose_name_plural = "Perfiles de pacientes"
        ordering = ["-creado_en"]

    def __str__(self):
        return "Paciente: {0}".format(self.usuario.nombre_completo)
