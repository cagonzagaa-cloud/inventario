from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from categorias.models import Categoria
from tributacion.models import ClasificacionTributaria
from tributacion.services import obtener_tarifa_general, obtener_tarifa_producto


class Producto(models.Model):

    @property
    def esta_bajo_stock(self):
        return self.stock <= self.stock_minimo

    codigo = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Código"
    )

    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre"
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos"
    )

    clasificacion_tributaria = models.ForeignKey(
        ClasificacionTributaria,
        on_delete=models.PROTECT,
        related_name="productos",
        blank=True,
        null=True,
        help_text="Clasificación tributaria explícita que determina la tarifa de IVA del producto."
    )

    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    precio = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    stock_minimo = models.PositiveIntegerField(
        default=5
    )

    estado = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        verbose_name = "Producto"

        verbose_name_plural = "Productos"

        ordering = ["nombre"]

    @property
    def tarifa_iva(self):
        if self.clasificacion_tributaria and self.clasificacion_tributaria.tarifa:
            tarifa = obtener_tarifa_producto(self, fecha_operacion=None)
            if tarifa:
                return tarifa.porcentaje
            return None

        tarifa_general = obtener_tarifa_general()
        return tarifa_general.porcentaje if tarifa_general else None

    @property
    def tarifa_iva_codigo(self):
        if self.clasificacion_tributaria and self.clasificacion_tributaria.tarifa:
            tarifa = obtener_tarifa_producto(self, fecha_operacion=None)
            if tarifa:
                return tarifa.codigo
            return None

        tarifa_general = obtener_tarifa_general()
        return tarifa_general.codigo if tarifa_general else None

    @property
    def tarifa_iva_descripcion(self):
        if self.clasificacion_tributaria and self.clasificacion_tributaria.tarifa:
            tarifa = obtener_tarifa_producto(self, fecha_operacion=None)
            if tarifa:
                return tarifa.descripcion
            return None

        tarifa_general = obtener_tarifa_general()
        return tarifa_general.descripcion if tarifa_general else None


    @property
    def valor_tributario(self):
        """Return the monetary tax value for the product's `precio` according to its IVA tarifa.

        Calculates `precio * (tarifa/100)` when tarifa is available, otherwise returns None.
        """
        try:
            porcentaje = self.tarifa_iva
            if porcentaje is None or self.precio is None:
                return None
            return (self.precio * Decimal(porcentaje) / Decimal('100')).quantize(Decimal('0.01'))
        except Exception:
            return None


    def __str__(self):

        return f"{self.codigo} - {self.nombre}"