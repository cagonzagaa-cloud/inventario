from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from reportes.utils import registrar_movimiento

from .models import Producto
from .forms import ProductoForm


@login_required
def lista_productos(request):

    productos = Producto.objects.select_related(
        "categoria",
        "clasificacion_tributaria"
    ).order_by("-id")

    form = ProductoForm()

    return render(
        request,
        "productos/lista.html",
        {
            "productos": productos,
            "form": form
        }
    )


@login_required
def crear_producto(request):

    if request.method == "POST":

        form = ProductoForm(request.POST)

        if form.is_valid():
            producto = form.save()

            if producto.stock > 0:
                registrar_movimiento(
                    producto=producto,
                    tipo="ENTRADA",
                    cantidad=producto.stock,
                    stock_anterior=0,
                    stock_nuevo=producto.stock,
                    usuario=request.user,
                    referencia=f"PROD-{producto.pk}",
                )

            messages.success(
                request,
                "Producto creado correctamente."
            )
            return redirect("lista_productos")

        messages.error(
            request,
            "Revise la información ingresada."
        )

    return redirect("lista_productos")


@login_required
def editar_producto(request, pk):

    producto = get_object_or_404(
        Producto,
        pk=pk
    )

    if request.method == "POST":

        stock_anterior = producto.stock
        form = ProductoForm(
            request.POST,
            instance=producto
        )

        if form.is_valid():
            producto_actualizado = form.save()
            diferencia = producto_actualizado.stock - stock_anterior

            if diferencia > 0:
                registrar_movimiento(
                    producto=producto_actualizado,
                    tipo="ENTRADA",
                    cantidad=diferencia,
                    stock_anterior=stock_anterior,
                    stock_nuevo=producto_actualizado.stock,
                    usuario=request.user,
                    referencia=f"PROD-{producto_actualizado.pk}",
                )
            elif diferencia < 0:
                registrar_movimiento(
                    producto=producto_actualizado,
                    tipo="SALIDA",
                    cantidad=abs(diferencia),
                    stock_anterior=stock_anterior,
                    stock_nuevo=producto_actualizado.stock,
                    usuario=request.user,
                    referencia=f"PROD-{producto_actualizado.pk}",
                )

            messages.success(
                request,
                "Producto actualizado correctamente."
            )
            return redirect("lista_productos")

        messages.error(
            request,
            "Revise la información."
        )

    return redirect("lista_productos")


@login_required
def eliminar_producto(request, pk):

    producto = get_object_or_404(
        Producto,
        pk=pk
    )

    producto.delete()

    messages.success(
        request,
        "Producto eliminado."
    )

    return redirect("lista_productos")