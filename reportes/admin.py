from django.contrib import admin

from .models import MovimientoInventario



@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):


    list_display = (

        "producto",

        "tipo",

        "cantidad",

        "stock_anterior",

        "stock_nuevo",

        "usuario",

        "fecha",

    )


    list_filter = (

        "tipo",

        "fecha",

    )


    search_fields = (

        "producto__nombre",

        "usuario__username",

    )