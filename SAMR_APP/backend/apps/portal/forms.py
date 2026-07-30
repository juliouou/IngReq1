"""Formularios de la app portal (Pantalla 1: Login y Registro)."""
from django import forms

from shared.validators import validar_cedula_ecuatoriana, validar_telefono
from apps.biometria.models import TipoDispositivo


DISPOSITIVO_CHOICES = (("", "Vincular mas tarde"),) + TipoDispositivo.CHOICES


INPUT_CLS = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
)


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electronico",
        widget=forms.EmailInput(attrs={
            "autofocus": True, "placeholder": "tu@correo.com", "class": INPUT_CLS,
        }),
    )
    password = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(attrs={"placeholder": "********", "class": INPUT_CLS}),
    )


class RegistroForm(forms.Form):
    nombres = forms.CharField(
        label="Nombres", max_length=120, widget=forms.TextInput(attrs={"class": INPUT_CLS})
    )
    apellidos = forms.CharField(
        label="Apellidos", max_length=120, widget=forms.TextInput(attrs={"class": INPUT_CLS})
    )
    cedula = forms.CharField(
        label="Cedula", max_length=10, widget=forms.TextInput(attrs={"class": INPUT_CLS})
    )
    afiliacion_iess = forms.CharField(
        label="N. de afiliacion IESS", max_length=50,
        widget=forms.TextInput(attrs={"class": INPUT_CLS}),
    )
    telefono = forms.CharField(
        label="Telefono", max_length=15, required=False,
        widget=forms.TextInput(attrs={"class": INPUT_CLS}),
    )
    email = forms.EmailField(
        label="Correo electronico", widget=forms.EmailInput(attrs={"class": INPUT_CLS})
    )
    password = forms.CharField(
        label="Contrasena", min_length=8,
        widget=forms.PasswordInput(attrs={"class": INPUT_CLS}),
    )
    password_confirmacion = forms.CharField(
        label="Confirmar contrasena", widget=forms.PasswordInput(attrs={"class": INPUT_CLS})
    )
    dispositivo_iot = forms.ChoiceField(
        label="Dispositivo IoT", choices=DISPOSITIVO_CHOICES, required=False,
        widget=forms.Select(attrs={"class": INPUT_CLS}),
    )
    consentimiento_lopdp = forms.BooleanField(
        label="Acepto el tratamiento de mis datos personales bajo la LOPDP",
        required=True,
        error_messages={"required": "Debes aceptar el consentimiento LOPDP para continuar."},
        widget=forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-teal-600"}),
    )

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"]
        try:
            validar_cedula_ecuatoriana(cedula)
        except forms.ValidationError:
            raise
        except Exception as exc:
            raise forms.ValidationError(str(exc))
        return cedula

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        if telefono:
            try:
                validar_telefono(telefono)
            except Exception as exc:
                raise forms.ValidationError(str(exc))
        return telefono

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirmacion = cleaned.get("password_confirmacion")
        if password and confirmacion and password != confirmacion:
            self.add_error("password_confirmacion", "Las contrasenas no coinciden.")
        return cleaned


class MFAForm(forms.Form):
    codigo = forms.CharField(
        label="Codigo de verificacion",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "autofocus": True, "inputmode": "numeric", "pattern": "[0-9]*",
            "placeholder": "000000", "autocomplete": "one-time-code",
            "class": INPUT_CLS + " text-center text-2xl tracking-[0.5em] font-mono",
        }),
    )
