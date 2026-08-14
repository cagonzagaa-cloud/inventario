from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from .forms import ConfiguracionSistemaForm
from .models import ConfiguracionSistema


def es_administrador(user):
    return user.is_authenticated and (
        user.is_superuser or getattr(user.perfil, "es_administrador", False)
    )


@login_required(login_url="login")
@user_passes_test(es_administrador, login_url="login")
def configuracion_sistema(request):
    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)

    if request.method == "POST":
        form = ConfiguracionSistemaForm(request.POST, instance=configuracion)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración actualizada correctamente.")
            return redirect("configuracion_sistema")
        messages.error(request, "Revise la información ingresada.")
    else:
        form = ConfiguracionSistemaForm(instance=configuracion)

    return render(
        request,
        "configuracion/index.html",
        {"form": form, "configuracion": configuracion},
    )
