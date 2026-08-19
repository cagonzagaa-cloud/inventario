from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EntradaForm, DetalleEntradaForm, DetalleEntradaFormSet
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
    formset = DetalleEntradaFormSet(prefix="detalles")

    contexto = {

        "entradas": entradas,

        "form": form,
        "formset": formset,

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
            formset = DetalleEntradaFormSet(request.POST, prefix="detalles")

            if form.is_valid() and formset.is_valid():

                try:
                    with transaction.atomic():
                        entrada = form.save(commit=False)
                        entrada.usuario = request.user
                        entrada.save()
                        formset.instance = entrada
                        formset.save()
                        entrada.confirmar(request.user)
                except Exception as exc:
                    messages.error(request, str(exc))
                    entradas = Entrada.objects.select_related("proveedor", "usuario").order_by("-id")
                    return render(request, "entradas/lista.html", {
                        "entradas": entradas, "form": form, "formset": formset,
                        "abrir_formulario": True,
                    }, status=400)
                messages.success(request, "Entrada guardada y confirmada correctamente.")
                return redirect("detalle_entrada", pk=entrada.pk)

            else:

                messages.error(
                    request,
                    "Verifique la información ingresada."
                )

        if request.method == "POST" and not (form.is_valid() and formset.is_valid()):
            entradas = Entrada.objects.select_related("proveedor", "usuario").order_by("-id")
            return render(request, "entradas/lista.html", {
                "entradas": entradas, "form": form, "formset": formset,
                "abrir_formulario": True,
            }, status=400)
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

    if entrada.estado != "BORRADOR":
        messages.warning(request, "Una entrada procesada no puede eliminarse. Use la opción Anular.")
        return redirect("lista_entradas")
    entrada.delete()

    messages.success(
        request,
        "Entrada eliminada correctamente."
    )

    return redirect(
        "lista_entradas"
    )



@login_required
def anular_entrada(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk)
    if request.method != "POST":
        messages.warning(request, "La anulación debe confirmarse desde el listado.")
        return redirect("lista_entradas")
    try:
        entrada.anular(request.user)
        messages.success(request, "Entrada anulada y stock revertido correctamente.")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("lista_entradas")


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
