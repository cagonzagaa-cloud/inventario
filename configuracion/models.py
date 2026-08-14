from django.db import models


class ConfiguracionSistema(models.Model):
    MONEDA_CHOICES = [
        ("USD", "Dólares"),
        ("EUR", "Euros"),
    ]

    nombre_empresa = models.CharField(max_length=200, default="Sistema de Inventario")
    rif = models.CharField(max_length=20, blank=True, default="")
    telefono = models.CharField(max_length=20, blank=True, default="")
    correo = models.EmailField(blank=True, default="")
    direccion = models.TextField(blank=True, default="")
    moneda = models.CharField(max_length=10, choices=MONEDA_CHOICES, default="USD")
    impuesto_iva = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stock_minimo_alerta = models.PositiveIntegerField(default=5)
    horario_atencion = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        verbose_name = "Configuración del sistema"
        verbose_name_plural = "Configuraciones del sistema"

    def __str__(self):
        return self.nombre_empresa
