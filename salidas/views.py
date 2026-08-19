from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from productos.models import Producto

from .forms import SalidaForm, DetalleSalidaForm, DetalleSalidaFormSet
from .models import Salida, DetalleSalida


# =====================================================
# LISTA DE SALIDAS
# =====================================================

@login_required
def lista_salidas(request):

    salidas = Salida.objects.select_related(
        "cliente",
        "usuario"
    ).order_by("-id")

    form = SalidaForm()
    formset = DetalleSalidaFormSet(prefix="detalles")

    contexto = {
        "salidas": salidas,
        "form": form,
        "formset": formset,
    }

    return render(
        request,
        "salidas/lista.html",
        contexto
    )


# =====================================================
# CREAR SALIDA
# =====================================================

@login_required
def crear_salida(request):

    if request.method == "POST":

        form = SalidaForm(request.POST)
        formset = DetalleSalidaFormSet(request.POST, prefix="detalles")

        if form.is_valid() and formset.is_valid():

            try:
                with transaction.atomic():
                    salida = form.save(commit=False)
                    salida.usuario = request.user
                    salida.save()
                    formset.instance = salida
                    formset.save()
                    salida.confirmar(request.user)
            except Exception as exc:
                messages.error(request, str(exc))
                salidas = Salida.objects.select_related("cliente", "usuario").order_by("-id")
                return render(request, "salidas/lista.html", {
                    "salidas": salidas, "form": form, "formset": formset,
                    "abrir_formulario": True,
                }, status=400)
            messages.success(request, "Salida guardada y confirmada correctamente.")
            return redirect("detalle_salida", pk=salida.pk)

        else:

            messages.error(
                request,
                "Verifique la información ingresada."
            )

    if request.method == "POST" and not (form.is_valid() and formset.is_valid()):
        salidas = Salida.objects.select_related("cliente", "usuario").order_by("-id")
        return render(request, "salidas/lista.html", {
            "salidas": salidas, "form": form, "formset": formset,
            "abrir_formulario": True,
        }, status=400)
    return redirect("lista_salidas")


# =====================================================
# EDITAR SALIDA
# =====================================================

@login_required
def editar_salida(request, pk):

    salida = get_object_or_404(
        Salida,
        pk=pk
    )

    if request.method == "POST":

        form = SalidaForm(
            request.POST,
            instance=salida
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Salida actualizada correctamente."
            )

        else:

            messages.error(
                request,
                "Verifique la información ingresada."
            )

    return redirect(
        "lista_salidas"
    )


# =====================================================
# ELIMINAR SALIDA
# =====================================================

@login_required
def eliminar_salida(request, pk):

    salida = get_object_or_404(
        Salida,
        pk=pk
    )

    if salida.estado != "BORRADOR":
        messages.warning(request, "Una salida procesada no puede eliminarse. Use la opción Anular.")
        return redirect("lista_salidas")
    salida.delete()

    messages.success(
        request,
        "Salida eliminada correctamente."
    )

    return redirect(
        "lista_salidas"
    )


# =====================================================
# DETALLE DE SALIDA
# =====================================================

@login_required
def anular_salida(request, pk):
    salida = get_object_or_404(Salida, pk=pk)
    if request.method != "POST":
        messages.warning(request, "La anulación debe confirmarse desde el listado.")
        return redirect("lista_salidas")
    try:
        salida.anular(request.user)
        messages.success(request, "Salida anulada y stock revertido correctamente.")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("lista_salidas")


@login_required
def detalle_salida(request, pk):

    salida = get_object_or_404(
        Salida.objects.select_related(
            "cliente",
            "usuario"
        ),
        pk=pk
    )


    productos = Producto.objects.filter(
        estado=True
    ).order_by("nombre")


    detalles = DetalleSalida.objects.select_related(
        "producto"
    ).filter(
        salida=salida
    ).order_by("id")


    form = DetalleSalidaForm()



    contexto = {

        "salida": salida,

        "detalles": detalles,

        "productos": productos,

        "form": form,

    }


    return render(
        request,
        "salidas/detalle.html",
        contexto
    )


# =====================================================
# AGREGAR DETALLE DE SALIDA
# =====================================================

@login_required
def agregar_detalle_salida(request, pk):

    salida = get_object_or_404(
        Salida,
        id=pk
    )

    if request.method == "POST":
        form = DetalleSalidaForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.salida = salida
            detalle.save()
            messages.success(request, "Producto agregado correctamente.")
        else:
            error = " ".join(item for errores in form.errors.values() for item in errores)
            messages.error(request, f"No se pudo agregar el producto. {error}")

        return redirect(
            "detalle_salida",
            pk=salida.id
        )

    return redirect(
        "detalle_salida",
        pk=salida.id
    )


@login_required
def eliminar_detalle_salida(request, pk):

    detalle = get_object_or_404(
        DetalleSalida,
        id=pk
    )


    salida_id = detalle.salida.id


    detalle.delete()


    messages.success(
        request,
        "Producto eliminado correctamente de la salida."
    )


    return redirect(
        "detalle_salida",
        pk=salida_id
    )

# =====================================================
# ELIMINAR DETALLE
# =====================================================

@login_required
def eliminar_detalle(request, pk):

    detalle = get_object_or_404(
        DetalleSalida,
        pk=pk
    )


    salida_id = detalle.salida.id


    detalle.delete()


    messages.success(
        request,
        "Producto eliminado correctamente."
    )


    return redirect(
        "detalle_salida",
        pk=salida_id
    )

# =====================================================
# OBTENER PRECIO DEL PRODUCTO
# =====================================================


@login_required
def obtener_precio_producto(request, pk):

    producto = get_object_or_404(
        Producto,
        pk=pk
    )


    return JsonResponse({

        "precio": float(producto.precio),

        "stock": producto.stock

    })


@login_required
def confirmar_salida(request, pk):
    salida = get_object_or_404(Salida, pk=pk)
    try:
        salida.confirmar(request.user)
        messages.success(request, "Salida confirmada correctamente.")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("detalle_salida", pk=salida.pk)
