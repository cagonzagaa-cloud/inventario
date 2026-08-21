from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.deletion import ProtectedError

from .models import Proveedor
from .forms import ProveedorForm


@login_required
def lista_proveedores(request):

    proveedores = Proveedor.objects.all().order_by("-id")

    form = ProveedorForm()

    return render(
        request,
        "proveedores/lista.html",
        {
            "proveedores": proveedores,
            "form": form
        }
    )


@login_required
def crear_proveedor(request):

    if request.method == "POST":

        form = ProveedorForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Proveedor registrado correctamente."
            )

        else:

            messages.error(
                request,
                "Revise la información ingresada."
            )

    return redirect("lista_proveedores")


@login_required
def editar_proveedor(request, pk):

    proveedor = get_object_or_404(
        Proveedor,
        pk=pk
    )

    if request.method == "POST":

        form = ProveedorForm(
            request.POST,
            instance=proveedor
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Proveedor actualizado correctamente."
            )

        else:

            messages.error(
                request,
                "Existen errores en el formulario."
            )

    return redirect("lista_proveedores")


@login_required
def eliminar_proveedor(request, pk):

    proveedor = get_object_or_404(
        Proveedor,
        pk=pk
    )

    if request.method != "POST":
        messages.warning(request, "Confirme la eliminación del proveedor desde el listado.")
        return redirect("lista_proveedores")

    try:
        proveedor.delete()
    except ProtectedError:
        proveedor.estado = False
        proveedor.save(update_fields=["estado"])
        messages.warning(request, "El proveedor tiene movimientos asociados y fue desactivado para conservar su historial.")
        return redirect("lista_proveedores")

    messages.success(
        request,
        "Proveedor eliminado correctamente."
    )

    return redirect("lista_proveedores")
