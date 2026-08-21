from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm
from .models import Cliente


@login_required
def lista_clientes(request):

    clientes = Cliente.objects.all().order_by("-id")

    form = ClienteForm()

    contexto = {

        "clientes": clientes,

        "form": form,

    }

    return render(
        request,
        "clientes/lista.html",
        contexto
    )


@login_required
def crear_cliente(request):

    if request.method == "POST":

        form = ClienteForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Cliente registrado correctamente."
            )

        else:

            messages.error(
                request,
                "Verifique la información ingresada."
            )

    return redirect("lista_clientes")


@login_required
def editar_cliente(request, pk):

    cliente = get_object_or_404(
        Cliente,
        pk=pk
    )

    if request.method == "POST":

        form = ClienteForm(
            request.POST,
            instance=cliente
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Cliente actualizado correctamente."
            )

        else:

            messages.error(
                request,
                "Verifique la información ingresada."
            )

    return redirect("lista_clientes")


@login_required
def eliminar_cliente(request, pk):

    cliente = get_object_or_404(
        Cliente,
        pk=pk
    )

    if request.method != "POST":
        messages.warning(request, "Confirme la desactivación del cliente desde el listado.")
        return redirect("lista_clientes")

    cliente.estado = False
    cliente.save(update_fields=["estado"])

    messages.success(
        request,
        "Cliente desactivado correctamente; su historial se conserva."
    )

    return redirect("lista_clientes")
