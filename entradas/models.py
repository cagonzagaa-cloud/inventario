from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

from productos.models import Producto
from proveedores.models import Proveedor
from tributacion.services import calcular_iva_detalle, obtener_porcentaje_iva_producto


class Entrada(models.Model):
    TIPOS_ENTRADA = [
        ("COMPRA", "Compra"),
        ("DEVOLUCION", "Devolución"),
        ("AJUSTE", "Ajuste de Inventario"),
        ("DONACION", "Donación"),
        ("OTRO", "Otro"),
    ]

    ESTADOS = [
        ("BORRADOR", "Borrador"),
        ("CONFIRMADA", "Confirmada"),
        ("ANULADA", "Anulada"),
    ]

    codigo = models.CharField(
        "Código",
        max_length=20,
        unique=True,
        editable=False
    )

    numero_documento = models.CharField(
        "N° Documento",
        max_length=50,
        blank=True,
        null=True
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="entradas",
        verbose_name="Proveedor"
    )

    fecha = models.DateField(
        verbose_name="Fecha de Entrada"
    )

    tipo = models.CharField(
        "Tipo de Entrada",
        max_length=20,
        choices=TIPOS_ENTRADA,
        default="COMPRA"
    )

    total = models.DecimalField(
        "Total",
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )

    estado = models.CharField(
        "Estado",
        max_length=15,
        choices=ESTADOS,
        default="BORRADOR"
    )

    observaciones = models.TextField(
        "Observaciones",
        blank=True,
        null=True
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="entradas"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def actualizar_total(self):

        total = sum(
            detalle.subtotal
            for detalle in self.detalles.all()
        )

        self.total = total

        super().save(update_fields=["total"])

    @property
    def total_base(self):
        from decimal import Decimal

        return sum(
            (detalle.base for detalle in self.detalles.all()),
            Decimal("0.00"),
        )

    @property
    def total_iva(self):
        from decimal import Decimal

        return sum(
            (detalle.iva for detalle in self.detalles.all()),
            Decimal("0.00"),
        )

    @property
    def total_con_iva(self):
        return self.total

    def __str__(self):

        return self.codigo

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ["-id"]

    def save(self, *args, **kwargs):

        if not self.codigo:

            ultima = Entrada.objects.order_by("-id").first()

            if ultima:

                numero = int(ultima.codigo.split("-")[1]) + 1

            else:

                numero = 1

            self.codigo = f"ENT-{numero:06d}"

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.codigo} - {self.proveedor.razon_social}"


class DetalleEntrada(models.Model):

    entrada = models.ForeignKey(
        Entrada,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalle_entradas"
    )

    cantidad = models.PositiveIntegerField(
        "Cantidad"
    )

    costo = models.DecimalField(
        "Costo Unitario",
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        "Subtotal",
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )

    class Meta:
        verbose_name = "Detalle de Entrada"
        verbose_name_plural = "Detalles de Entrada"

    @property
    def base(self):
        return Decimal(self.cantidad) * Decimal(str(self.costo))

    @property
    def tarifa(self):
        if self.entrada and self.entrada.fecha:
            return obtener_porcentaje_iva_producto(self.producto, self.entrada.fecha)
        return obtener_porcentaje_iva_producto(self.producto)

    @property
    def iva(self):
        _, iva, _ = calcular_iva_detalle(
            self.cantidad,
            self.costo,
            self.tarifa,
        )
        return iva

    @property
    def total_con_iva(self):
        _, _, total = calcular_iva_detalle(
            self.cantidad,
            self.costo,
            self.tarifa,
        )
        return total

    def save(self, *args, **kwargs):

        self.subtotal = self.total_con_iva

        super().save(*args, **kwargs)

        self.entrada.actualizar_total()

    def __str__(self):

        return f"{self.entrada.codigo} - {self.producto.nombre}"
    
    