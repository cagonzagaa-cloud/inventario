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

            "codigo_barras": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: 7501234567890",
                    "autocomplete": "off"
                }
            ),

            "lote": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: LOTE-2026-001",
                    "autocomplete": "off"
                }
            ),

            "ubicacion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Bodega A / Pasillo 2 / Estante 4"
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

    def clean_codigo_barras(self):
        codigo = self.cleaned_data.get("codigo_barras")
        return codigo.strip() if codigo else None

    def clean_lote(self):
        return (self.cleaned_data.get("lote") or "").strip().upper()

    def clean_ubicacion(self):
        return (self.cleaned_data.get("ubicacion") or "").strip()

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
