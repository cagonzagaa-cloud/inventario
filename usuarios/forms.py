from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import PerfilUsuario


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su usuario"
            }
        )
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su contraseña"
            }
        )
    )


class UsuarioForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Usuario",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Nombres",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Apellidos",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        required=False,
        label="Correo",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        required=False,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        required=False,
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    rol = forms.ChoiceField(
        choices=PerfilUsuario.Rol.choices,
        label="Rol",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Usuario activo",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        existentes = get_user_model().objects.filter(username__iexact=username)
        if self.instance:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError("Ya existe un usuario con este nombre.")
        return username

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        if instance:
            self.fields["username"].initial = instance.username
            self.fields["first_name"].initial = instance.first_name
            self.fields["last_name"].initial = instance.last_name
            self.fields["email"].initial = instance.email
            self.fields["rol"].initial = instance.perfil.rol
            self.fields["is_active"].initial = instance.is_active

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
            if len(password1 or "") < 6:
                raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")

        if self.instance is None and not password1:
            raise forms.ValidationError("La contraseña es obligatoria para crear un usuario.")

        return cleaned_data

    def save(self, commit=True):
        user_model = get_user_model()
        if self.instance:
            user = self.instance
        else:
            user = user_model.objects.create_user(
                username=self.cleaned_data["username"],
                email=self.cleaned_data.get("email") or "",
                password=self.cleaned_data["password1"],
                first_name=self.cleaned_data.get("first_name") or "",
                last_name=self.cleaned_data.get("last_name") or "",
            )

        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data.get("first_name") or ""
        user.last_name = self.cleaned_data.get("last_name") or ""
        user.email = self.cleaned_data.get("email") or ""
        user.is_active = self.cleaned_data.get("is_active", False)

        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
            user.perfil.rol = self.cleaned_data["rol"]
            user.perfil.save(update_fields=["rol"])

        return user
