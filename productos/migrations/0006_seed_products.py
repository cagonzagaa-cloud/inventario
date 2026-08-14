from django.db import migrations


def create_seed_products(apps, schema_editor):
    Producto = apps.get_model('productos', 'Producto')
    Categoria = apps.get_model('categorias', 'Categoria')

    cat, _ = Categoria.objects.get_or_create(nombre='Varios')

    for i in range(1, 26):
        codigo = f'SEED-{i:03d}'
        nombre = f'Producto Seed {i}'
        Producto.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'categoria': cat,
                'costo': '1.00',
                'precio': '2.00',
                'stock': 10,
            }
        )


def delete_seed_products(apps, schema_editor):
    Producto = apps.get_model('productos', 'Producto')
    Producto.objects.filter(codigo__startswith='SEED-').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0005_producto_clasificacion_tributaria'),
    ]

    operations = [
        migrations.RunPython(create_seed_products, delete_seed_products),
    ]
