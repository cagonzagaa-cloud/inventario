from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = (

        "codigo",

        "codigo_barras",

        "nombre",

        "categoria",

        "clasificacion_tributaria",

        "tarifa_iva",

        "precio",

        "stock",

        "ubicacion",

        "lote",

        "estado",

    )

    list_filter = (

        "categoria",

        "clasificacion_tributaria",

        "estado",

    )

    search_fields = (

        "codigo",

        "codigo_barras",

        "lote",

        "ubicacion",

        "nombre",

        "clasificacion_tributaria__nombre",

    )
