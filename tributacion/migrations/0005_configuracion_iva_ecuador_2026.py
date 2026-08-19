from datetime import date

from django.db import migrations


def configurar_iva(apps, schema_editor):
    TarifaIVA = apps.get_model("tributacion", "TarifaIVA")
    Clasificacion = apps.get_model("tributacion", "ClasificacionTributaria")
    ReglaTemporal = apps.get_model("tributacion", "ReglaTemporalIVA")

    datos = {
        "IVA_0": ("0.00", date(2024, 4, 1), None,
                  "Transferencias con tarifa 0%; no equivale a exención.", "Arts. 55 y 56 LRTI"),
        "IVA_5": ("5.00", date(2024, 4, 1), None,
                  "Transferencia local de materiales incluidos en el listado oficial.",
                  "Resolución NAC-DGERCGC24-00000013"),
        "IVA_15": ("15.00", date(2024, 4, 1), None,
                   "Tarifa general vigente.", "Circular NAC-DGECCGC25-00000006"),
        "IVA_8_TUR": ("8.00", date(2026, 5, 23), date(2026, 5, 25),
                      "Reducción temporal para servicios turísticos habilitados.", "Decreto Ejecutivo 391"),
    }
    tarifas = {}
    for codigo, (porcentaje, inicio, fin, descripcion, norma) in datos.items():
        tarifa, _ = TarifaIVA.objects.update_or_create(
            codigo=codigo,
            defaults={"porcentaje": porcentaje, "fecha_inicio": inicio, "fecha_fin": fin,
                      "descripcion": descripcion, "referencia_normativa": norma,
                      "activo": True, "es_temporal": codigo == "IVA_8_TUR"},
        )
        tarifas[codigo] = tarifa

    Clasificacion.objects.update_or_create(
        codigo="MATERIAL_CONSTRUCCION_LISTADO_5",
        defaults={"nombre": "Material de construcción incluido en listado SRI",
                  "descripcion": "Solo productos expresamente incluidos; la categoría comercial no basta.",
                  "tarifa_id": tarifas["IVA_5"].id, "requiere_documentacion": True,
                  "fundamento_legal": "Resolución NAC-DGERCGC24-00000013",
                  "es_material_construccion_listado": True},
    )
    # Las clasificaciones 0% preexistentes requieren respaldo específico del producto.
    Clasificacion.objects.filter(tarifa_id=tarifas["IVA_0"].id).update(
        requiere_documentacion=True, fundamento_legal="Arts. 55 o 56 LRTI, según corresponda"
    )
    ReglaTemporal.objects.update_or_create(
        codigo="TURISMO_PICHINCHA_2026",
        defaults={"tarifa_id": tarifas["IVA_8_TUR"].id, "fecha_inicio": date(2026, 5, 23),
                  "fecha_fin": date(2026, 5, 25), "actividad": "TURISMO",
                  "referencia_normativa": "Decreto Ejecutivo 391", "activo": True,
                  "requiere_registro_turismo": True, "requiere_licencia_anual": True},
    )


class Migration(migrations.Migration):
    dependencies = [("tributacion", "0004_clasificaciontributaria_codigo_oficial_and_more")]
    operations = [migrations.RunPython(configurar_iva, migrations.RunPython.noop)]
