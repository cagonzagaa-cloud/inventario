from django import forms
from django.utils import timezone

from .models import Entrada, DetalleEntrada


class EntradaForm(forms.ModelForm):

    class Meta:
        model = Entrada

        fields = [
            "fecha",
            "proveedor",
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

            "proveedor": forms.Select(
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
                    "placeholder": "Observaciones de la entrada...",
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


class DetalleEntradaForm(forms.ModelForm):

    class Meta:
        model = DetalleEntrada

        fields = [
            "producto",
            "cantidad",
            "costo",
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

            "costo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),

        }

    def clean_cantidad(self):

        cantidad = self.cleaned_data["cantidad"]

        if cantidad <= 0:

            raise forms.ValidationError(
                "La cantidad debe ser mayor a cero."
            )

        return cantidad

    def clean_costo(self):

        costo = self.cleaned_data["costo"]

        if costo <= 0:

            raise forms.ValidationError(
                "El costo debe ser mayor a cero."
            )

        return costo