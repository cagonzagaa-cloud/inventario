from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render, get_object_or_404

from .forms import LoginForm, UsuarioForm
from .models import PerfilUsuario


def es_administrador(user):
    return user.is_authenticated and (
        user.is_superuser or getattr(user.perfil, "es_administrador", False)
    )


class LoginSistema(LoginView):
    template_name = "authentication/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True


class LogoutSistema(LogoutView):

    next_page = "login"

    def dispatch(self, request, *args, **kwargs):

        messages.success(
            request,
            "La sesión se cerró correctamente."
        )

        return super().dispatch(request, *args, **kwargs)


@login_required(login_url="login")
@user_passes_test(es_administrador, login_url="login")
def lista_usuarios(request):
    usuarios = get_user_model().objects.select_related("perfil").order_by("username")
    form = UsuarioForm()
    return render(request, "usuarios/lista.html", {"usuarios": usuarios, "form": form})


@login_required(login_url="login")
@user_passes_test(es_administrador, login_url="login")
def crear_usuario(request):
    usuarios = get_user_model().objects.select_related("perfil").order_by("username")
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente.")
            return redirect("lista_usuarios")
        messages.error(request, "Revise los datos del formulario.")
        return render(request, "usuarios/lista.html", {"usuarios": usuarios, "form": form})
    return render(request, "usuarios/lista.html", {"usuarios": usuarios, "form": UsuarioForm()})


@login_required(login_url="login")
@user_passes_test(es_administrador, login_url="login")
def editar_usuario(request, pk):
    usuario = get_object_or_404(get_user_model(), pk=pk)
    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("lista_usuarios")
        messages.error(request, "Revise los datos del formulario.")
        return render(request, "usuarios/editar.html", {"form": form, "usuario": usuario})

    form = UsuarioForm(instance=usuario)
    return render(request, "usuarios/editar.html", {"form": form, "usuario": usuario})


@login_required(login_url="login")
@user_passes_test(es_administrador, login_url="login")
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(get_user_model(), pk=pk)
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect("lista_usuarios")

    usuario.delete()
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect("lista_usuarios")