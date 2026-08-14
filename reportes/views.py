from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import MovimientoInventario
from django.http import JsonResponse
from django.core import serializers


@login_required
def kardex(request):

    movimientos = MovimientoInventario.objects.select_related(
        "producto",
        "usuario"
    ).order_by("-fecha")

    # Allow optional filtering by product via GET param `producto`
    producto_id = request.GET.get('producto')
    if producto_id:
        movimientos = movimientos.filter(producto__pk=producto_id)

    contexto = {
        "movimientos": movimientos
    }


    return render(
        request,
        "reportes/kardex.html",
        contexto
    )


@login_required
def api_ultimos_movimientos(request):
    """Return JSON list of recent movements. Supports optional `producto` GET param."""
    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').order_by('-fecha')[:50]
    producto_id = request.GET.get('producto')
    if producto_id:
        movimientos = movimientos.filter(producto__pk=producto_id)

    data = []
    for m in movimientos:
        data.append({
            'id': m.pk,
            'producto': m.producto.nombre,
            'producto_id': m.producto.pk,
            'tipo': m.tipo,
            'cantidad': m.cantidad,
            'fecha': m.fecha.strftime('%d/%m/%Y %H:%M'),
            'referencia': m.referencia,
            'detail_url': m.get_detail_url(),
            'stock_anterior': m.stock_anterior,
            'stock_nuevo': m.stock_nuevo,
            'usuario': getattr(m.usuario, 'username', None),
        })

    return JsonResponse({'movimientos': data})