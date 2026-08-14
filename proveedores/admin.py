from django.contrib import admin
from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "razon_social",
        "identificacion",
        "contacto",
        "telefono",
        "correo",
        "ciudad",
        "condicion_pago",
        "estado",
    )

    list_filter = (
        "estado",
        "tipo_identificacion",
        "condicion_pago",
        "provincia",
        "ciudad",
    )

    search_fields = (
        "codigo",
        "razon_social",
        "identificacion",
        "nombre_comercial",
        "contacto",
        "correo",
    )

    ordering = (
        "razon_social",
    )

    list_per_page = 15

    readonly_fields = (
        "fecha_creacion",
    )

    fieldsets = (

        ("Información General", {

            "fields": (
                "codigo",
                "tipo_identificacion",
                "identificacion",
                "razon_social",
                "nombre_comercial",
            )

        }),

        ("Información de Contacto", {

            "fields": (
                "contacto",
                "cargo",
                "telefono",
                "celular",
                "correo",
                "sitio_web",
            )

        }),

        ("Ubicación", {

            "fields": (
                "direccion",
                "provincia",
                "canton",
                "ciudad",
                "codigo_postal",
            )

        }),

        ("Información Comercial", {

            "fields": (
                "condicion_pago",
                "cupo_credito",
                "estado",
            )

        }),

        ("Información adicional", {

            "fields": (
                "observaciones",
                "fecha_creacion",
            )

        }),

    )