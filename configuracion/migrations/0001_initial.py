from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ConfiguracionSistema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_empresa', models.CharField(default='Sistema de Inventario', max_length=200)),
                ('rif', models.CharField(blank=True, default='', max_length=20)),
                ('telefono', models.CharField(blank=True, default='', max_length=20)),
                ('correo', models.EmailField(blank=True, default='')),
                ('direccion', models.TextField(blank=True, default='')),
                ('moneda', models.CharField(choices=[('USD', 'Dólares'), ('EUR', 'Euros')], default='USD', max_length=10)),
                ('impuesto_iva', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('stock_minimo_alerta', models.PositiveIntegerField(default=5)),
                ('horario_atencion', models.CharField(blank=True, default='', max_length=100)),
            ],
            options={
                'verbose_name': 'Configuración del sistema',
                'verbose_name_plural': 'Configuraciones del sistema',
            },
        ),
    ]
