from django.contrib import admin

from .models import TarifaIVA, ClasificacionTributaria


@admin.register(TarifaIVA)
class TarifaIVAAdmin(admin.ModelAdmin):
    list_display = ["codigo", "porcentaje", "activo", "fecha_inicio", "fecha_fin", "es_temporal"]
    list_filter = ["activo", "es_temporal"]
    search_fields = ["codigo", "descripcion"]


@admin.register(ClasificacionTributaria)
class ClasificacionTributariaAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "tarifa", "requiere_documentacion"]
    list_filter = ["tarifa", "requiere_documentacion"]
    search_fields = ["codigo", "nombre", "descripcion"]
