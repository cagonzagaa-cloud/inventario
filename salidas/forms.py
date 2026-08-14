from django import forms
from django.utils import timezone

from .models import Salida, DetalleSalida


class SalidaForm(forms.ModelForm):

    class Meta:

        model = Salida

        fields = [
            "fecha",
            "cliente",
            "numero_documento",
            "tipo",
            "estado",
            "observaciones",
        ]

        widgets = {

            "fecha": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "cliente": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "numero_documento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: FAC-001-00012345",
                }
            ),

            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "estado": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observaciones de la salida...",
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if not self.instance.pk:

            self.fields["fecha"].initial = timezone.now().date()

    def clean_numero_documento(self):

        documento = self.cleaned_data["numero_documento"]

        if documento:

            documento = documento.strip().upper()

        return documento

    def clean_fecha(self):

        fecha = self.cleaned_data["fecha"]

        if fecha > timezone.now().date():

            raise forms.ValidationError(
                "La fecha no puede ser mayor a la fecha actual."
            )

        return fecha


class DetalleSalidaForm(forms.ModelForm):

    class Meta:

        model = DetalleSalida

        fields = [
            "producto",
            "cantidad",
            "precio",
        ]

        widgets = {

            "producto": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "precio": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),

        }

    def clean_cantidad(self):

        cantidad = self.cleaned_data["cantidad"]
        producto = self.cleaned_data.get("producto")

        if cantidad <= 0:
            raise forms.ValidationError(
                "La cantidad debe ser mayor a cero."
            )

        if producto and cantidad > producto.stock:
            raise forms.ValidationError(
                f"Solo existen {producto.stock} unidades disponibles."
            )

        return cantidad

    def clean_precio(self):

        precio = self.cleaned_data["precio"]

        if precio <= 0:
            raise forms.ValidationError(
                "El precio debe ser mayor a cero."
            )

        return precio