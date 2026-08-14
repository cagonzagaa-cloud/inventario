from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (

        "identificacion",

        "nombres",

        "apellidos",

        "telefono",

        "correo",

        "estado",

    )

    list_filter = (

        "tipo_identificacion",

        "estado",

    )

    search_fields = (

        "identificacion",

        "nombres",

        "apellidos",

        "telefono",

        "correo",

    )

    list_per_page = 10

    ordering = (

        "apellidos",

        "nombres",

    )