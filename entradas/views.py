from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EntradaForm, DetalleEntradaForm
from .models import Entrada, DetalleEntrada
from productos.models import Producto
from reportes.utils import registrar_movimiento




@login_required
def lista_entradas(request):

    entradas = Entrada.objects.select_related(
        "proveedor",
        "usuario"
    ).order_by("-id")

    form = EntradaForm()

    contexto = {

        "entradas": entradas,

        "form": form,

    }

    return render(
        request,
        "entradas/lista.html",
        contexto
    )


@login_required
def crear_entrada(request):

        if request.method == "POST":

            form = EntradaForm(request.POST)

            if form.is_valid():

                entrada = form.save(commit=False)

                entrada.usuario = request.user

                entrada.save()

                messages.success(request, "Entrada creada correctamente. Ahora agregue los productos.")
                return redirect("detalle_entrada", pk=entrada.pk)

            else:

                messages.error(
                    request,
                    "Verifique la información ingresada."
                )

        return redirect("lista_entradas")


@login_required
def editar_entrada(request, pk):

    entrada = get_object_or_404(
        Entrada,
        pk=pk
    )


    if request.method == "POST":

        form = EntradaForm(
            request.POST,
            instance=entrada
        )


        if form.is_valid():

            entrada = form.save(commit=False)

            entrada.usuario = request.user

            entrada.save()


            messages.success(
                request,
                "Entrada actualizada correctamente."
            )

            return redirect(
                "lista_entradas"
            )


    else:

        form = EntradaForm(
            instance=entrada
        )


    entradas = Entrada.objects.select_related(
        "proveedor",
        "usuario"
    ).order_by("-id")


    contexto = {

        "entradas": entradas,

        "form": form,

        "editar": True,

        "entrada": entrada

    }


    return render(
        request,
        "entradas/lista.html",
        contexto
    )


@login_required
def eliminar_entrada(request, pk):

    entrada = get_object_or_404(
        Entrada,
        pk=pk
    )

    entrada.delete()

    messages.success(
        request,
        "Entrada eliminada correctamente."
    )

    return redirect(
        "lista_entradas"
    )



@login_required
def detalle_entrada(request, pk):

    entrada = get_object_or_404(
        Entrada.objects.select_related(
            "proveedor",
            "usuario"
        ),
        pk=pk
    )


    productos = Producto.objects.filter(
        estado=True
    ).order_by(
        "nombre"
    )


    detalles = DetalleEntrada.objects.select_related(
        "producto"
    ).filter(
        entrada=entrada
    ).order_by(
        "id"
    )


    contexto = {

        "entrada": entrada,

        "detalles": detalles,

        "productos": productos,

        "form": DetalleEntradaForm(),

    }


    return render(
        request,
        "entradas/detalle.html",
        contexto
    )



@login_required
def agregar_detalle_entrada(request, pk):

    entrada = get_object_or_404(
        Entrada,
        pk=pk
    )


    if request.method == "POST":
        form = DetalleEntradaForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.entrada = entrada
            detalle.save()
            messages.success(request, "Producto agregado correctamente.")
        else:
            error = " ".join(item for errores in form.errors.values() for item in errores)
            messages.error(request, f"No se pudo agregar el producto. {error}")


    return redirect(
        "detalle_entrada",
        pk=entrada.id
    )

@login_required
def editar_detalle(request, pk):

    detalle = get_object_or_404(
        DetalleEntrada,
        pk=pk
    )


    entrada = detalle.entrada


    if request.method == "POST":
        form = DetalleEntradaForm(request.POST, instance=detalle)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
        else:
            error = " ".join(item for errores in form.errors.values() for item in errores)
            messages.error(request, f"No se pudo actualizar el producto. {error}")


    return redirect(
        "detalle_entrada",
        pk=entrada.id
    )

@transaction.atomic
def confirmar_entrada(request, pk):

    entrada = get_object_or_404(
        Entrada,
        pk=pk
    )


    if entrada.estado != "BORRADOR":

        messages.warning(
            request,
            "La entrada ya fue procesada."
        )

        return redirect(
            "detalle_entrada",
            pk=entrada.id
        )


    try:
        entrada.confirmar(request.user)
    except Exception as exc:
        messages.error(request, str(exc))
        return redirect("detalle_entrada", pk=entrada.id)


    messages.success(
        request,
        "Entrada confirmada correctamente."
    )


    return redirect(
        "detalle_entrada",
        pk=entrada.id
    )



@login_required
def eliminar_detalle_entrada(request, pk):

    detalle = get_object_or_404(
        DetalleEntrada,
        pk=pk
    )


    entrada = detalle.entrada


    detalle.delete()


    entrada.actualizar_total()


    messages.success(
        request,
        "Producto eliminado correctamente."
    )


    return redirect(
        "detalle_entrada",
        pk=entrada.id
    )
