import calendar
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Sum
from django.shortcuts import render
from django.utils import timezone

from categorias.models import Categoria
from entradas.models import Entrada
from productos.models import Producto
from proveedores.models import Proveedor
from reportes.models import MovimientoInventario
from salidas.models import Salida


@login_required(login_url='login')
def dashboard(request):
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    total_proveedores = Proveedor.objects.count()
    productos_bajo_stock = list(
        Producto.objects.filter(stock__lte=F("stock_minimo")).order_by("stock", "nombre")[:5]
    )
    stock_bajo = len(productos_bajo_stock)

    today = timezone.now().date()
    labels = []
    entradas_series = []
    salidas_series = []

    for offset in range(5, -1, -1):
        month_number = today.month - offset
        year = today.year

        while month_number <= 0:
            month_number += 12
            year -= 1

        while month_number > 12:
            month_number -= 12
            year += 1

        labels.append(f"{calendar.month_abbr[month_number]} {year}")

        total_entrada = Entrada.objects.filter(
            fecha__year=year,
            fecha__month=month_number,
        ).aggregate(total=Sum("total"))["total"] or Decimal("0")

        total_salida = Salida.objects.filter(
            fecha__year=year,
            fecha__month=month_number,
        ).aggregate(total=Sum("total"))["total"] or Decimal("0")

        entradas_series.append(float(total_entrada))
        salidas_series.append(float(total_salida))

    productos_por_categoria = list(
        Producto.objects.values("categoria__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    distribution_labels = [
        item["categoria__nombre"] or "Sin categoría"
        for item in productos_por_categoria
    ]
    distribution_data = [item["total"] for item in productos_por_categoria]

    if not distribution_labels:
        distribution_labels = ["Sin datos"]
        distribution_data = [0]

    ultimos_movimientos = MovimientoInventario.objects.select_related(
        "producto",
        "usuario",
    ).order_by("-fecha")[:8]

    context = {
        "productos": total_productos,
        "categorias": total_categorias,
        "proveedores": total_proveedores,
        "stock_bajo": stock_bajo,
        "productos_bajo_stock": productos_bajo_stock,
        "dashboard_data": {
            "labels": labels,
            "entradas": entradas_series,
            "salidas": salidas_series,
        },
        "distribution_data": {
            "labels": distribution_labels,
            "data": distribution_data,
        },
        "ultimos_movimientos": ultimos_movimientos,
    }

    return render(request, "dashboard/index.html", context)