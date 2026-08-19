from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

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
    max_intentos = 5
    bloqueo_segundos = 900

    def _segundos_restantes(self):
        bloqueado_hasta = self.request.session.get("login_bloqueado_hasta", 0)
        return max(0, int(bloqueado_hasta - timezone.now().timestamp()))

    def post(self, request, *args, **kwargs):
        restantes = self._segundos_restantes()
        if restantes:
            form = self.get_form()
            form.add_error(None, f"Demasiados intentos fallidos. Intente nuevamente en {max(1, restantes // 60 + 1)} minutos.")
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        # No incrementar otra vez cuando la petición ya estaba bloqueada.
        if not self._segundos_restantes():
            intentos = self.request.session.get("login_intentos", 0) + 1
            self.request.session["login_intentos"] = intentos
            restantes = self.max_intentos - intentos
            if restantes <= 0:
                self.request.session["login_bloqueado_hasta"] = (
                    timezone.now().timestamp() + self.bloqueo_segundos
                )
                form.add_error(None, "Alcanzó el máximo de 5 intentos. El acceso queda bloqueado durante 15 minutos.")
            else:
                form.add_error(None, f"Credenciales incorrectas. Le quedan {restantes} intentos.")
        return super().form_invalid(form)

    def form_valid(self, form):
        self.request.session.pop("login_intentos", None)
        self.request.session.pop("login_bloqueado_hasta", None)
        return super().form_valid(form)


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
    if request.method != "POST":
        messages.warning(request, "Confirme la desactivación desde el listado de usuarios.")
        return redirect("lista_usuarios")
    if usuario == request.user:
        messages.error(request, "No puedes desactivar tu propio usuario.")
        return redirect("lista_usuarios")

    usuario.is_active = False
    usuario.save(update_fields=["is_active"])
    messages.success(request, "Usuario desactivado correctamente; su historial se conserva.")
    return redirect("lista_usuarios")
