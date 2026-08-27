from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone

from tributacion.services import calcular_iva_detalle, obtener_porcentaje_iva_producto

from clientes.models import Cliente
from productos.models import Producto

from reportes.utils import registrar_movimiento


class Salida(models.Model):


    TIPOS_SALIDA = [

        ("VENTA", "Venta"),
        ("DEVOLUCION", "Devolución"),
        ("AJUSTE", "Ajuste de Inventario"),
        ("CONSUMO", "Consumo Interno"),
        ("OTRO", "Otro"),

    ]


    ESTADOS = [

        ("BORRADOR", "Borrador"),
        ("CONFIRMADA", "Confirmada"),
        ("ANULADA", "Anulada"),

    ]


    codigo = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )


    numero_documento = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )


    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="salidas"
    )


    fecha = models.DateField(default=timezone.localdate)



    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_SALIDA,
        default="VENTA"
    )


    total = models.DecimalField(
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
                                             related_name="salidas_confirmadas", editable=False)
    operacion_tributaria = models.BooleanField(default=True)
    actividad_tributaria = models.CharField(max_length=80, blank=True)
    tiene_registro_turismo = models.BooleanField(default=False)
    tiene_licencia_anual = models.BooleanField(default=False)


    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default="BORRADOR"
    )


    observaciones = models.TextField(
        blank=True,
        null=True
    )


    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="salidas"
    )


    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )



    class Meta:

        verbose_name = "Salida"

        verbose_name_plural = "Salidas"

        ordering = ["-id"]



    def save(self, *args, **kwargs):

        if self.pk:
            anterior = Salida.objects.filter(pk=self.pk).only("estado").first()
            if anterior and anterior.estado != "BORRADOR" and self.estado == anterior.estado:
                raise ValidationError("Una salida confirmada o anulada no puede modificarse directamente.")

        if not self.codigo:


            ultimo = Salida.objects.order_by("-id").first()


            if ultimo:

                numero = int(
                    ultimo.codigo.replace("SAL-", "")
                ) + 1


            else:

                numero = 1



            self.codigo = f"SAL-{numero:05d}"



        super().save(*args, **kwargs)




    def actualizar_total(self):
        detalles = self.detalles.all()
        self.subtotal_general = sum((d.subtotal for d in detalles), Decimal("0.00"))
        self.iva_total = sum((d.valor_iva for d in detalles), Decimal("0.00"))
        self.total = self.subtotal_general + self.iva_total
        super().save(update_fields=["subtotal_general", "iva_total", "total"])



    @property
    def total_base(self):
        return sum(
            (detalle.subtotal for detalle in self.detalles.all()),
            Decimal("0.00"),
        )

    @property
    def total_iva(self):
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

    def delete(self, *args, **kwargs):
        if self.estado != "BORRADOR":
            raise ValidationError("Las salidas procesadas no se eliminan; deben anularse.")
        return super().delete(*args, **kwargs)

    @transaction.atomic
    def confirmar(self, usuario):
        if self.estado != "BORRADOR":
            raise ValidationError("Solo se puede confirmar una salida en borrador.")
        detalles = list(self.detalles.select_related("producto", "producto__clasificacion_tributaria__tarifa"))
        if not detalles:
            raise ValidationError("La salida debe contener al menos un producto.")
        for detalle in detalles:
            detalle.calcular_y_fijar()
            producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)
            if producto.stock < detalle.cantidad:
                raise ValidationError(f"Stock insuficiente para {producto.nombre}.")
            anterior = producto.stock
            producto.stock -= detalle.cantidad
            producto.save(update_fields=["stock"])
            registrar_movimiento(producto, "SALIDA", detalle.cantidad, anterior, producto.stock,
                                 usuario, self.codigo)
        self.actualizar_total()
        self.estado = "CONFIRMADA"
        self.fecha_confirmacion = timezone.now()
        self.usuario_confirmacion = usuario
        super().save(update_fields=["estado", "fecha_confirmacion", "usuario_confirmacion"])
        from telegram_bot.models import Notificacion
        from telegram_bot.services import crear_notificacion
        crear_notificacion(
            Notificacion.Tipo.SALIDA,
            "Salida confirmada",
            f"{self.codigo} fue confirmada por {usuario.get_full_name() or usuario.username}. Total: ${self.total}",
            f"/salidas/detalle/{self.pk}/",
        )

    @transaction.atomic
    def anular(self, usuario):
        if self.estado != "CONFIRMADA":
            raise ValidationError("Solo se puede anular una salida confirmada.")
        for detalle in self.detalles.all():
            producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)
            anterior = producto.stock
            producto.stock += detalle.cantidad
            producto.save(update_fields=["stock"])
            registrar_movimiento(producto, "ENTRADA", detalle.cantidad, anterior, producto.stock,
                                 usuario, f"ANUL-{self.codigo}")
        self.estado, self.fecha_anulacion = "ANULADA", timezone.now()
        super().save(update_fields=["estado", "fecha_anulacion"])





class DetalleSalida(models.Model):


    salida = models.ForeignKey(
        Salida,
        on_delete=models.CASCADE,
        related_name="detalles"
    )


    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalle_salidas"
    )


    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])


    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2, validators=[MinValueValidator(0)]
    )


    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    valor_iva = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    total_linea = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    codigo_tarifa_iva = models.CharField(max_length=20, blank=True, editable=False)


    @property
    def base(self):
        return Decimal(self.cantidad) * Decimal(str(self.precio))

    @property
    def tarifa(self):
        if self.pk:
            return self.porcentaje_iva
        if self.salida and self.salida.fecha:
            return obtener_porcentaje_iva_producto(self.producto, self.salida.fecha)
        return obtener_porcentaje_iva_producto(self.producto)

    @property
    def iva(self):
        return self.valor_iva

    @property
    def total_con_iva(self):
        return self.total_linea

    def calcular_y_fijar(self):
        from tributacion.services import resolver_tarifa
        tarifa = resolver_tarifa(
            self.producto, self.salida.fecha,
            operacion_tributaria=self.salida.operacion_tributaria,
            actividad=self.salida.actividad_tributaria or None,
            tiene_registro_turismo=self.salida.tiene_registro_turismo,
            tiene_licencia_anual=self.salida.tiene_licencia_anual,
        )
        if tarifa is None and self.salida.operacion_tributaria:
            raise ValidationError(f"No existe una tarifa vigente verificable para {self.producto}.")
        porcentaje = tarifa.porcentaje if tarifa else Decimal("0.00")
        self.subtotal, self.valor_iva, self.total_linea = calcular_iva_detalle(
            self.cantidad, self.precio, porcentaje)
        self.porcentaje_iva = porcentaje
        self.codigo_tarifa_iva = tarifa.codigo if tarifa else "NO_OBJETO"
        super().save(update_fields=["subtotal", "valor_iva", "total_linea", "porcentaje_iva", "codigo_tarifa_iva"])

    class Meta:

        verbose_name = "Detalle de Salida"

        verbose_name_plural = "Detalles de Salida"




    @transaction.atomic
    def save(self, *args, **kwargs):
        cantidad = int(self.cantidad)
        precio = Decimal(str(self.precio))

        self.cantidad = cantidad
        self.precio = precio

        if self.salida.estado != "BORRADOR":
            raise ValidationError("No se pueden modificar detalles de una salida procesada.")
        from tributacion.services import resolver_tarifa
        tarifa_obj = resolver_tarifa(
            self.producto, self.salida.fecha,
            operacion_tributaria=self.salida.operacion_tributaria,
            actividad=self.salida.actividad_tributaria or None,
            tiene_registro_turismo=self.salida.tiene_registro_turismo,
            tiene_licencia_anual=self.salida.tiene_licencia_anual,
        )
        if tarifa_obj is None and self.salida.operacion_tributaria:
            raise ValidationError("El producto no tiene una tarifa vigente verificable.")
        tarifa = tarifa_obj.porcentaje if tarifa_obj else Decimal("0.00")
        self.subtotal, self.valor_iva, self.total_linea = calcular_iva_detalle(cantidad, precio, tarifa)
        self.porcentaje_iva = tarifa
        self.codigo_tarifa_iva = tarifa_obj.codigo if tarifa_obj else "NO_OBJETO"



        super().save(
            *args,
            **kwargs
        )



        self.salida.actualizar_total()





    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.salida.estado != "BORRADOR":
            raise ValidationError("No se pueden eliminar detalles de una salida procesada.")

        salida = self.salida

        result = super().delete(*args, **kwargs)
        salida.actualizar_total()
        return result




    def __str__(self):

        return (

            f"{self.salida.codigo} - "

            f"{self.producto.nombre}"

        )
