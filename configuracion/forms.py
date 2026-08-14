from django import forms

from .models import ConfiguracionSistema


class ConfiguracionSistemaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSistema
        fields = [
            "nombre_empresa",
            "rif",
            "telefono",
            "correo",
            "direccion",
            "moneda",
            "impuesto_iva",
            "stock_minimo_alerta",
            "horario_atencion",
        ]
        widgets = {
            "nombre_empresa": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Inventario Plus"}),
            "rif": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 1790000001001"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "0999999999"}),
            "correo": forms.EmailInput(attrs={"class": "form-control", "placeholder": "soporte@empresa.com"}),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "moneda": forms.Select(attrs={"class": "form-select"}),
            "impuesto_iva": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "stock_minimo_alerta": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
            "horario_atencion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Lun - Vie 08:00 - 18:00"}),
        }

    def clean_rif(self):
        rif = (self.cleaned_data.get("rif") or "").strip().upper()
        return rif

    def clean_nombre_empresa(self):
        nombre = (self.cleaned_data.get("nombre_empresa") or "").strip()
        return nombre
