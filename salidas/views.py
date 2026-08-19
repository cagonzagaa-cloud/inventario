from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from productos.models import Producto

from .forms import SalidaForm, DetalleSalidaForm
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

    contexto = {
        "salidas": salidas,
        "form": form,
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

        if form.is_valid():

            salida = form.save(commit=False)

            salida.usuario = request.user

            salida.save()

            messages.success(request, "Salida creada correctamente. Ahora agregue los productos.")
            return redirect("detalle_salida", pk=salida.pk)

        else:

            messages.error(
                request,
                "Verifique la información ingresada."
            )

    return redirect(
        "lista_salidas"
    )


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
