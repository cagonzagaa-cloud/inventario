from django import forms
from .models import Categoria

class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = "__all__"

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese el nombre de la categoría"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ingrese una descripción"
            }),
            "estado": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"]

        if len(nombre.strip()) < 3:
            raise forms.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )

        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data["descripcion"]

        if len(descripcion.strip()) < 5:
            raise forms.ValidationError(
                "La descripción debe tener al menos 5 caracteres."
            )

        return descripcion