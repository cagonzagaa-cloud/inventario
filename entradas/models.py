from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
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
        verbose_name="Fecha de Entrada",
        default=timezone.localdate,
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
    subtotal_general = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    iva_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, editable=False)
    fecha_anulacion = models.DateTimeField(null=True, blank=True, editable=False)
    usuario_confirmacion = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT,
                                             related_name="entradas_confirmadas", editable=False)
    operacion_tributaria = models.BooleanField(default=True)

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
        detalles = self.detalles.all()
        self.subtotal_general = sum((d.subtotal for d in detalles), Decimal("0.00"))
        self.iva_total = sum((d.valor_iva for d in detalles), Decimal("0.00"))
        self.total = self.subtotal_general + self.iva_total
        super().save(update_fields=["subtotal_general", "iva_total", "total"])

    @property
    def total_base(self):
        from decimal import Decimal

        return sum(
            (detalle.subtotal for detalle in self.detalles.all()),
            Decimal("0.00"),
        )

    @property
    def total_iva(self):
        from decimal import Decimal

        return sum(
            (detalle.valor_iva for detalle in self.detalles.all()),
            Decimal("0.00"),
        )

    @property
    def total_con_iva(self):
        return self.total

    @property
    def desglose_tributario(self):
        from tributacion.services import obtener_desglose
        return obtener_desglose(self.detalles.all())

    def __str__(self):

        return self.codigo

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ["-id"]

    def save(self, *args, **kwargs):

        if self.pk:
            anterior = Entrada.objects.filter(pk=self.pk).only("estado").first()
            if anterior and anterior.estado != "BORRADOR" and self.estado == anterior.estado:
                raise ValidationError("Una entrada confirmada o anulada no puede modificarse directamente.")

        if not self.codigo:

            ultima = Entrada.objects.order_by("-id").first()

            if ultima:

                numero = int(ultima.codigo.split("-")[1]) + 1

            else:

                numero = 1

            self.codigo = f"ENT-{numero:06d}"

        super().save(*args, **kwargs)

    @transaction.atomic
    def confirmar(self, usuario):
        if self.estado != "BORRADOR":
            raise ValidationError("Solo se puede confirmar una entrada en borrador.")
        detalles = list(self.detalles.select_related("producto", "producto__clasificacion_tributaria__tarifa"))
        if not detalles:
            raise ValidationError("La entrada debe contener al menos un producto.")
        from reportes.utils import registrar_movimiento
        for detalle in detalles:
            detalle.calcular_y_fijar()
            producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)
            anterior = producto.stock
            producto.stock += detalle.cantidad
            producto.save(update_fields=["stock"])
            registrar_movimiento(producto, "ENTRADA", detalle.cantidad, anterior, producto.stock,
                                 usuario, self.codigo)
        self.actualizar_total()
        self.estado = "CONFIRMADA"
        self.fecha_confirmacion = timezone.now()
        self.usuario_confirmacion = usuario
        super().save(update_fields=["estado", "fecha_confirmacion", "usuario_confirmacion"])
        from telegram_bot.models import Notificacion
        from telegram_bot.services import crear_notificacion
        crear_notificacion(
            Notificacion.Tipo.ENTRADA,
            "Entrada confirmada",
            f"{self.codigo} fue confirmada por {usuario.get_full_name() or usuario.username}. Total: ${self.total}",
            f"/entradas/detalle/{self.pk}/",
        )

    @transaction.atomic
    def anular(self, usuario):
        if self.estado != "CONFIRMADA":
            raise ValidationError("Solo se puede anular una entrada confirmada.")
        from reportes.utils import registrar_movimiento
        for detalle in self.detalles.all():
            producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)
            if producto.stock < detalle.cantidad:
                raise ValidationError(f"No se puede revertir {producto}: el stock ya fue consumido.")
            anterior = producto.stock
            producto.stock -= detalle.cantidad
            producto.save(update_fields=["stock"])
            registrar_movimiento(producto, "SALIDA", detalle.cantidad, anterior, producto.stock,
                                 usuario, f"ANUL-{self.codigo}")
        self.estado, self.fecha_anulacion = "ANULADA", timezone.now()
        super().save(update_fields=["estado", "fecha_anulacion"])

    def __str__(self):

        return f"{self.codigo} - {self.proveedor.razon_social}"

    def delete(self, *args, **kwargs):
        if self.estado != "BORRADOR":
            raise ValidationError("Las entradas procesadas no se eliminan; deben anularse.")
        return super().delete(*args, **kwargs)


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
        "Cantidad", validators=[MinValueValidator(1)]
    )

    costo = models.DecimalField(
        "Costo Unitario",
        max_digits=10,
        decimal_places=2, validators=[MinValueValidator(0)]
    )

    subtotal = models.DecimalField(
        "Subtotal",
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    valor_iva = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    total_linea = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    codigo_tarifa_iva = models.CharField(max_length=20, blank=True, editable=False)

    class Meta:
        verbose_name = "Detalle de Entrada"
        verbose_name_plural = "Detalles de Entrada"

    @property
    def base(self):
        return Decimal(self.cantidad) * Decimal(str(self.costo))

    @property
    def tarifa(self):
        if self.pk:
            return self.porcentaje_iva
        if self.entrada and self.entrada.fecha:
            return obtener_porcentaje_iva_producto(self.producto, self.entrada.fecha)
        return obtener_porcentaje_iva_producto(self.producto)

    @property
    def iva(self):
        return self.valor_iva

    @property
    def total_con_iva(self):
        return self.total_linea

    def calcular_y_fijar(self):
        from tributacion.services import resolver_tarifa
        tarifa = resolver_tarifa(self.producto, self.entrada.fecha,
                                  operacion_tributaria=self.entrada.operacion_tributaria)
        if tarifa is None and self.entrada.operacion_tributaria:
            raise ValidationError(f"No existe una tarifa vigente verificable para {self.producto}.")
        porcentaje = tarifa.porcentaje if tarifa else Decimal("0.00")
        self.subtotal, self.valor_iva, self.total_linea = calcular_iva_detalle(
            self.cantidad, self.costo, porcentaje)
        self.porcentaje_iva = porcentaje
        self.codigo_tarifa_iva = tarifa.codigo if tarifa else "NO_OBJETO"
        super().save(update_fields=["subtotal", "valor_iva", "total_linea", "porcentaje_iva", "codigo_tarifa_iva"])

    def save(self, *args, **kwargs):
        if self.entrada.estado != "BORRADOR":
            raise ValidationError("No se pueden modificar detalles de una entrada procesada.")
        from tributacion.services import resolver_tarifa
        tarifa_obj = resolver_tarifa(self.producto, self.entrada.fecha,
                                      operacion_tributaria=self.entrada.operacion_tributaria)
        if tarifa_obj is None and self.entrada.operacion_tributaria:
            raise ValidationError("El producto no tiene una tarifa vigente verificable.")
        tarifa = tarifa_obj.porcentaje if tarifa_obj else Decimal("0.00")
        self.subtotal, self.valor_iva, self.total_linea = calcular_iva_detalle(self.cantidad, self.costo, tarifa)
        self.porcentaje_iva = tarifa
        self.codigo_tarifa_iva = tarifa_obj.codigo if tarifa_obj else "NO_OBJETO"
        super().save(*args, **kwargs)

        self.entrada.actualizar_total()

    def __str__(self):

        return f"{self.entrada.codigo} - {self.producto.nombre}"

    def delete(self, *args, **kwargs):
        if self.entrada.estado != "BORRADOR":
            raise ValidationError("No se pueden eliminar detalles de una entrada procesada.")
        entrada = self.entrada
        result = super().delete(*args, **kwargs)
        entrada.actualizar_total()
        return result
    
