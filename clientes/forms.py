from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):

    class Meta:

        model = Cliente

        fields = [

            "tipo_identificacion",

            "identificacion",

            "nombres",

            "apellidos",

            "telefono",

            "correo",

            "direccion",

            "estado",

        ]

        widgets = {

            "tipo_identificacion": forms.Select(

                attrs={
                    "class": "form-select"
                }

            ),

            "identificacion": forms.TextInput(

                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese la identificación"
                }

            ),

            "nombres": forms.TextInput(

                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese los nombres"
                }

            ),

            "apellidos": forms.TextInput(

                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese los apellidos"
                }

            ),

            "telefono": forms.TextInput(

                attrs={
                    "class": "form-control",
                    "placeholder": "0999999999"
                }

            ),

            "correo": forms.EmailInput(

                attrs={
                    "class": "form-control",
                    "placeholder": "correo@ejemplo.com"
                }

            ),

            "direccion": forms.TextInput(

                attrs={
                    "class": "form-control",
                    "placeholder": "Dirección del cliente"
                }

            ),

            "estado": forms.CheckboxInput(

                attrs={
                    "class": "form-check-input"
                }

            ),

        }

    # ==========================
    # VALIDACIONES
    # ==========================

    def clean_identificacion(self):

        identificacion = self.cleaned_data["identificacion"].strip()

        if len(identificacion) < 10:

            raise forms.ValidationError(
                "La identificación no es válida."
            )

        return identificacion


    def clean_nombres(self):

        nombres = self.cleaned_data["nombres"].strip()

        if len(nombres) < 2:

            raise forms.ValidationError(
                "Ingrese un nombre válido."
            )

        return nombres


    def clean_apellidos(self):

        apellidos = self.cleaned_data["apellidos"].strip()

        if len(apellidos) < 2:

            raise forms.ValidationError(
                "Ingrese un apellido válido."
            )

        return apellidos