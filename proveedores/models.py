from django.db import models


class Proveedor(models.Model):

    TIPO_IDENTIFICACION = [
        ("RUC", "RUC"),
        ("CEDULA", "Cédula"),
        ("PASAPORTE", "Pasaporte"),
    ]

    CONDICION_PAGO = [
        ("CONTADO", "Contado"),
        ("15", "15 días"),
        ("30", "30 días"),
        ("60", "60 días"),
        ("90", "90 días"),
    ]

    codigo = models.CharField(
        max_length=15,
        unique=True
    )

    tipo_identificacion = models.CharField(
        max_length=15,
        choices=TIPO_IDENTIFICACION,
        default="RUC"
    )

    identificacion = models.CharField(
        max_length=13,
        unique=True
    )

    razon_social = models.CharField(
        max_length=200
    )

    nombre_comercial = models.CharField(
        max_length=200,
        blank=True
    )

    contacto = models.CharField(
        max_length=150
    )

    cargo = models.CharField(
        max_length=100,
        blank=True
    )

    telefono = models.CharField(
        max_length=20
    )

    celular = models.CharField(
        max_length=20,
        blank=True
    )

    correo = models.EmailField()

    sitio_web = models.URLField(
        blank=True
    )

    direccion = models.TextField()

    provincia = models.CharField(
        max_length=100
    )

    canton = models.CharField(
        max_length=100
    )

    ciudad = models.CharField(
        max_length=100
    )

    codigo_postal = models.CharField(
        max_length=15,
        blank=True
    )

    condicion_pago = models.CharField(
        max_length=15,
        choices=CONDICION_PAGO,
        default="CONTADO"
    )

    cupo_credito = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    observaciones = models.TextField(
        blank=True
    )

    estado = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["razon_social"]
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.codigo} - {self.razon_social}"