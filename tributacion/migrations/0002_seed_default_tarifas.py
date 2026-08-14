from datetime import date

from django.db import migrations


def create_default_tarifas(apps, schema_editor):
    TarifaIVA = apps.get_model("tributacion", "TarifaIVA")

    TarifaIVA.objects.update_or_create(
        codigo="IVA_0",
        defaults={
            "porcentaje": "0.00",
            "descripcion": "Bienes y servicios exentos de IVA.",
            "fecha_inicio": date(2020, 1, 1),
            "fecha_fin": None,
            "activo": True,
            "es_temporal": False,
        },
    )

    TarifaIVA.objects.update_or_create(
        codigo="IVA_5",
        defaults={
            "porcentaje": "5.00",
            "descripcion": "Tarifa reducida de IVA para bienes y servicios gravados con 5%.",
            "fecha_inicio": date(2020, 1, 1),
            "fecha_fin": None,
            "activo": True,
            "es_temporal": False,
        },
    )

    TarifaIVA.objects.update_or_create(
        codigo="IVA_15",
        defaults={
            "porcentaje": "15.00",
            "descripcion": "Tarifa general de IVA vigente en Ecuador.",
            "fecha_inicio": date(2020, 1, 1),
            "fecha_fin": None,
            "activo": True,
            "es_temporal": False,
        },
    )

    TarifaIVA.objects.update_or_create(
        codigo="IVA_8_TUR",
        defaults={
            "porcentaje": "8.00",
            "descripcion": "Tarifa temporal de IVA para actividades turísticas.",
            "fecha_inicio": date(2023, 1, 1),
            "fecha_fin": None,
            "activo": False,
            "es_temporal": True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("tributacion", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_tarifas),
    ]
