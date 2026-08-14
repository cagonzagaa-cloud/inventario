from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = "__all__"

        widgets = {

            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: PROD-001",
                    "autocomplete": "off"
                }
            ),

            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese el nombre del producto",
                    "autocomplete": "off"
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Descripción del producto"
                }
            ),

            "categoria": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "clasificacion_tributaria": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "costo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "0.00"
                }
            ),

            "precio": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "0.00"
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0"
                }
            ),

            "stock_minimo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0"
                }
            ),

            "estado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            )

        }

    def clean_costo(self):

        costo = self.cleaned_data["costo"]

        if costo < 0:
            raise forms.ValidationError(
                "El costo no puede ser negativo."
            )

        return costo

    def clean_precio(self):

        precio = self.cleaned_data["precio"]

        if precio < 0:
            raise forms.ValidationError(
                "El precio no puede ser negativo."
            )

        return precio

    def clean_stock(self):

        stock = self.cleaned_data["stock"]

        if stock < 0:
            raise forms.ValidationError(
                "El stock no puede ser negativo."
            )

        return stock

    def clean_stock_minimo(self):

        minimo = self.cleaned_data["stock_minimo"]

        if minimo < 0:
            raise forms.ValidationError(
                "El stock mínimo no puede ser negativo."
            )

        return minimo