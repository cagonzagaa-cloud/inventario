from datetime import date

from django.db import migrations


def create_default_clasificaciones(apps, schema_editor):
    TarifaIVA = apps.get_model("tributacion", "TarifaIVA")
    ClasificacionTributaria = apps.get_model("tributacion", "ClasificacionTributaria")

    tarifa_0 = TarifaIVA.objects.get(codigo="IVA_0")
    tarifa_15 = TarifaIVA.objects.get(codigo="IVA_15")

    ClasificacionTributaria.objects.update_or_create(
        codigo="ALIMENTOS_PROCESADOS_15",
        defaults={
            "nombre": "Alimentos procesados y bebidas gravadas",
            "descripcion": (
                "Productos alimenticios sometidos a procesos industriales, "
                "bebidas procesadas, panadería, carnes procesadas y snacks."
            ),
            "tarifa_id": tarifa_15.id,
            "requiere_documentacion": False,
        },
    )

    ClasificacionTributaria.objects.update_or_create(
        codigo="TECNOLOGIA_ELECTRODOMESTICOS_15",
        defaults={
            "nombre": "Tecnología y electrodomésticos gravados",
            "descripcion": (
                "Electrónica, equipos de computación, línea blanca, software y "
                "bienes para el hogar gravados con tarifa general 15%."
            ),
            "tarifa_id": tarifa_15.id,
            "requiere_documentacion": False,
        },
    )

    ClasificacionTributaria.objects.update_or_create(
        codigo="MODA_CUIDADO_PERSONAL_15",
        defaults={
            "nombre": "Ropa, calzado y cuidado personal gravados",
            "descripcion": (
                "Prendas, calzado, accesorios, cosméticos y artículos personales "
                "gravados con tarifa general de IVA."
            ),
            "tarifa_id": tarifa_15.id,
            "requiere_documentacion": False,
        },
    )

    ClasificacionTributaria.objects.update_or_create(
        codigo="AUTOMOTRIZ_TRANSPORTE_15",
        defaults={
            "nombre": "Sector automotriz y transporte gravados",
            "descripcion": (
                "Vehículos, repuestos, mantenimiento, lubricantes y pasajes gravados "
                "con tarifa general de IVA."
            ),
            "tarifa_id": tarifa_15.id,
            "requiere_documentacion": False,
        },
    )

    ClasificacionTributaria.objects.update_or_create(
        codigo="ENTRETENIMIENTO_SNACKS_15",
        defaults={
            "nombre": "Entretenimiento, snacks y servicios gravados",
            "descripcion": (
                "Suscripciones de streaming, eventos, restaurantes, snacks y "
                "productos preparados gravados con tarifa general."
            ),
            "tarifa_id": tarifa_15.id,
            "requiere_documentacion": False,
        },
    )

    ClasificacionTributaria.objects.update_or_create(
        codigo="BASICOS_0",
        defaults={
            "nombre": "Productos básicos de canasta básica con tarifa 0%",
            "descripcion": (
                "Alimentos esenciales en estado natural y otros bienes de primera "
                "necesidad exentos de IVA."
            ),
            "tarifa_id": tarifa_0.id,
            "requiere_documentacion": False,
        },
    )

    ClasificacionTributaria.objects.update_or_create(
        codigo="SALUD_EDUCACION_0",
        defaults={
            "nombre": "Salud y educación con tarifa 0%",
            "descripcion": (
                "Medicamentos, insumos médicos, libros y útiles escolares con "
                "tarifa 0% de IVA."
            ),
            "tarifa_id": tarifa_0.id,
            "requiere_documentacion": False,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("tributacion", "0002_seed_default_tarifas"),
    ]

    operations = [
        migrations.RunPython(create_default_clasificaciones),
    ]
