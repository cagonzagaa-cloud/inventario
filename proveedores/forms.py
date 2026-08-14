from django import forms
from django.core.exceptions import ValidationError
from .models import Proveedor


class ProveedorForm(forms.ModelForm):

    class Meta:
        model = Proveedor
        fields = "__all__"

        widgets = {

            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: PROV-0001"
            }),

            "tipo_identificacion": forms.Select(attrs={
                "class": "form-select"
            }),

            "identificacion": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese el RUC o Cédula"
            }),

            "razon_social": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Razón Social"
            }),

            "nombre_comercial": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre Comercial"
            }),

            "contacto": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Persona de contacto"
            }),

            "cargo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Cargo"
            }),

            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "0999999999"
            }),

            "celular": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "0999999999"
            }),

            "correo": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "correo@empresa.com"
            }),

            "sitio_web": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://empresa.com"
            }),

            "direccion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "provincia": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "canton": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "ciudad": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "codigo_postal": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "condicion_pago": forms.Select(attrs={
                "class": "form-select"
            }),

            "cupo_credito": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01"
            }),

            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),

            "estado": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),

        }

    # ==========================
    # VALIDACIONES
    # ==========================

    def clean_codigo(self):

        codigo = self.cleaned_data["codigo"].strip().upper()

        if len(codigo) < 4:
            raise ValidationError(
                "El código es demasiado corto."
            )

        return codigo


    def clean_identificacion(self):

        identificacion = self.cleaned_data["identificacion"].strip()

        if not identificacion.isdigit():

            raise ValidationError(
                "La identificación solo puede contener números."
            )

        if len(identificacion) not in [10, 13]:

            raise ValidationError(
                "Debe ingresar una cédula (10 dígitos) o un RUC (13 dígitos)."
            )

        return identificacion


    def clean_correo(self):

        correo = self.cleaned_data["correo"].lower()

        return correo


    def clean_telefono(self):

        telefono = self.cleaned_data["telefono"].strip()

        if not telefono.isdigit():

            raise ValidationError(
                "El teléfono solo debe contener números."
            )

        return telefono


    def clean_celular(self):

        celular = self.cleaned_data.get("celular")

        if celular:

            celular = celular.strip()

            if not celular.isdigit():

                raise ValidationError(
                    "El celular solo debe contener números."
                )

        return celular


    def clean_cupo_credito(self):

        cupo = self.cleaned_data["cupo_credito"]

        if cupo < 0:

            raise ValidationError(
                "El cupo de crédito no puede ser negativo."
            )

        return cupo


    def clean_razon_social(self):

        razon = self.cleaned_data["razon_social"].strip().upper()

        return razon


    def clean_nombre_comercial(self):

        nombre = self.cleaned_data["nombre_comercial"].strip().upper()

        return nombre