from django.contrib import admin

from .models import Entrada, DetalleEntrada


class DetalleEntradaInline(admin.TabularInline):
    model = DetalleEntrada

    extra = 1

    fields = (
        "producto",
        "cantidad",
        "costo",
        "subtotal",
    )

    readonly_fields = (
        "subtotal",
    )


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "fecha",
        "proveedor",
        "numero_documento",
        "tipo",
        "estado",
        "total",
        "usuario",
    )

    list_filter = (
        "estado",
        "tipo",
        "fecha",
    )

    search_fields = (
        "codigo",
        "numero_documento",
        "proveedor__razon_social",
    )

    readonly_fields = (
        "codigo",
        "fecha",
        "total",
        "fecha_creacion",
    )

    ordering = (
        "-id",
    )

    date_hierarchy = "fecha"

    inlines = [
        DetalleEntradaInline,
    ]


@admin.register(DetalleEntrada)
class DetalleEntradaAdmin(admin.ModelAdmin):

    list_display = (
        "entrada",
        "producto",
        "cantidad",
        "costo",
        "subtotal",
    )

    list_filter = (
        "producto",
    )

    search_fields = (
        "entrada__codigo",
        "producto__nombre",
    )

    readonly_fields = (
        "subtotal",
    )
