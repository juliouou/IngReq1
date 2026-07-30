"""Configuracion del admin para la app usuarios."""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from apps.usuarios.models import PerfilMedico, PerfilPaciente, Usuario


class UsuarioCreationForm(forms.ModelForm):
    """Formulario de creacion de usuario en el admin (con confirmacion)."""

    password1 = forms.CharField(label="Contrasena", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirmar contrasena", widget=forms.PasswordInput
    )

    class Meta:
        model = Usuario
        fields = ("email", "nombres", "apellidos", "rol")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contrasenas no coinciden.")
        return p2

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password1"])
        if commit:
            usuario.save()
        return usuario


class UsuarioChangeForm(forms.ModelForm):
    """Formulario de edicion de usuario en el admin."""

    password = ReadOnlyPasswordHashField(label="Contrasena")

    class Meta:
        model = Usuario
        fields = (
            "email", "password", "nombres", "apellidos", "cedula", "telefono",
            "rol", "is_active", "is_staff", "is_superuser",
            "groups", "user_permissions",
        )


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    ordering = ("email",)
    list_display = ("email", "nombres", "apellidos", "rol", "is_active", "is_staff")
    list_filter = ("rol", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "nombres", "apellidos", "cedula")
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {
            "fields": ("nombres", "apellidos", "cedula", "telefono", "rol"),
        }),
        ("Permisos", {
            "fields": (
                "is_active", "is_staff", "is_superuser",
                "groups", "user_permissions",
            ),
        }),
        ("Fechas", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "nombres", "apellidos", "rol",
                "password1", "password2",
            ),
        }),
    )


@admin.register(PerfilMedico)
class PerfilMedicoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "especialidad", "numero_registro", "disponible")
    list_filter = ("disponible", "especialidad")
    search_fields = ("usuario__nombres", "usuario__apellidos", "numero_registro")


@admin.register(PerfilPaciente)
class PerfilPacienteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo_sangre", "fecha_nacimiento")
    list_filter = ("tipo_sangre",)
    search_fields = ("usuario__nombres", "usuario__apellidos")
