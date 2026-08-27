from django.contrib import admin

from .models import Salida, DetalleSalida


class DetalleSalidaInline(admin.TabularInline):

    model = DetalleSalida

    extra = 1

    readonly_fields = ("subtotal",)


@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):

    list_display = (

        "codigo",

        "fecha",

        "cliente",

        "tipo",

        "total",

        "estado",

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

        "cliente__razon_social",

    )

    readonly_fields = (

        "codigo",

        "fecha",

        "total",

        "fecha_creacion",

    )

    inlines = [

        DetalleSalidaInline

    ]


@admin.register(DetalleSalida)
class DetalleSalidaAdmin(admin.ModelAdmin):

    list_display = (

        "salida",

        "producto",

        "cantidad",

        "precio",

        "subtotal",

    )

    search_fields = (

        "salida__codigo",

        "producto__nombre",

    )
