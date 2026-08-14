from django.db import models


class Cliente(models.Model):

    TIPO_IDENTIFICACION = [

        ("CEDULA", "Cédula"),
        ("RUC", "RUC"),
        ("PASAPORTE", "Pasaporte"),

    ]

    tipo_identificacion = models.CharField(
        "Tipo de Identificación",
        max_length=20,
        choices=TIPO_IDENTIFICACION,
        default="CEDULA"
    )

    identificacion = models.CharField(
        "Número de Identificación",
        max_length=20,
        unique=True
    )

    nombres = models.CharField(
        "Nombres",
        max_length=100
    )

    apellidos = models.CharField(
        "Apellidos",
        max_length=100
    )

    telefono = models.CharField(
        "Teléfono",
        max_length=20,
        blank=True,
        null=True
    )

    correo = models.EmailField(
        "Correo Electrónico",
        blank=True,
        null=True
    )

    direccion = models.CharField(
        "Dirección",
        max_length=255,
        blank=True,
        null=True
    )

    estado = models.BooleanField(
        "Activo",
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        verbose_name = "Cliente"

        verbose_name_plural = "Clientes"

        ordering = ["apellidos", "nombres"]

    @property
    def nombre_completo(self):

        return f"{self.nombres} {self.apellidos}"

    def __str__(self):

        return f"{self.identificacion} - {self.nombres} {self.apellidos}"