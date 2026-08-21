from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import Entrada, DetalleEntrada
from proveedores.models import Proveedor
from productos.models import Producto


class EntradaForm(forms.ModelForm):

    class Meta:
        model = Entrada

        fields = [
            "fecha",
            "proveedor",
            "numero_documento",
            "tipo",
            "operacion_tributaria",
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

            "operacion_tributaria": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
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
            self.fields["fecha"].initial = timezone.localdate()

        self.fields["operacion_tributaria"].label = "Aplicar impuestos (IVA)"
        self.fields["operacion_tributaria"].help_text = "Desactive únicamente para operaciones no sujetas a impuestos."
        self.fields["proveedor"].queryset = Proveedor.objects.filter(estado=True).order_by("razon_social")
        self.fields["proveedor"].empty_label = "Seleccione un proveedor..."

    def clean_numero_documento(self):

        documento = self.cleaned_data["numero_documento"]

        if documento:
            documento = documento.strip().upper()

        return documento

    def clean_fecha(self):

        fecha = self.cleaned_data["fecha"]

        if fecha > timezone.localdate():

            raise forms.ValidationError(
                "La fecha no puede ser mayor a la fecha actual."
            )

        return fecha


class DetalleEntradaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = Producto.objects.filter(estado=True).order_by("nombre")
        self.fields["producto"].empty_label = "Busque y seleccione un producto..."

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
                    "value": 1,
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


DetalleEntradaFormSet = inlineformset_factory(
    Entrada,
    DetalleEntrada,
    form=DetalleEntradaForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
