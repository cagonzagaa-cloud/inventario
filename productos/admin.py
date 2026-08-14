from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = (

        "codigo",

        "nombre",

        "categoria",

        "clasificacion_tributaria",

        "tarifa_iva",

        "precio",

        "stock",

        "estado",

    )

    list_filter = (

        "categoria",

        "clasificacion_tributaria",

        "estado",

    )

    search_fields = (

        "codigo",

        "nombre",

        "clasificacion_tributaria__nombre",

    )