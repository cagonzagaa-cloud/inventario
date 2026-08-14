from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum

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


    fecha = models.DateField()



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


        total = self.detalles.aggregate(
            total=Sum("subtotal")
        )["total"]


        if total is None:

            total = Decimal("0.00")



        self.total = total


        super().save(
            update_fields=["total"]
        )



    @property
    def total_base(self):
        return sum(
            (detalle.base for detalle in self.detalles.all()),
            Decimal("0.00"),
        )

    @property
    def total_iva(self):
        return sum(
            (detalle.iva for detalle in self.detalles.all()),
            Decimal("0.00"),
        )

    @property
    def total_con_iva(self):
        return self.total

    def __str__(self):
        return self.codigo





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


    cantidad = models.PositiveIntegerField()


    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )


    @property
    def base(self):
        return Decimal(self.cantidad) * Decimal(str(self.precio))

    @property
    def tarifa(self):
        if self.salida and self.salida.fecha:
            return obtener_porcentaje_iva_producto(self.producto, self.salida.fecha)
        return obtener_porcentaje_iva_producto(self.producto)

    @property
    def iva(self):
        _, iva, _ = calcular_iva_detalle(
            self.cantidad,
            self.precio,
            self.tarifa,
        )
        return iva

    @property
    def total_con_iva(self):
        _, _, total = calcular_iva_detalle(
            self.cantidad,
            self.precio,
            self.tarifa,
        )
        return total

    class Meta:

        verbose_name = "Detalle de Salida"

        verbose_name_plural = "Detalles de Salida"




    @transaction.atomic
    def save(self, *args, **kwargs):
        cantidad = int(self.cantidad)
        precio = Decimal(str(self.precio))

        self.cantidad = cantidad
        self.precio = precio

        # ===========================
        # NUEVA SALIDA
        # ===========================

        if not self.pk:

            stock_anterior = self.producto.stock

            if self.producto.stock < cantidad:
                raise ValueError(
                    f"No existe stock suficiente de {self.producto.nombre}"
                )

            self.producto.stock -= cantidad

            self.producto.save(
                update_fields=["stock"]
            )



            registrar_movimiento(

                producto=self.producto,

                tipo="SALIDA",

                cantidad=cantidad,

                stock_anterior=stock_anterior,

                stock_nuevo=self.producto.stock,

                usuario=self.salida.usuario,

                referencia=self.salida.codigo

            )



        # ===========================
        # EDITAR DETALLE
        # ===========================

        else:

            anterior = DetalleSalida.objects.get(
                pk=self.pk
            )

            diferencia = cantidad - anterior.cantidad

            stock_anterior = self.producto.stock

            if diferencia > 0:

                if self.producto.stock < diferencia:
                    raise ValueError(
                        f"No existe stock suficiente de {self.producto.nombre}"
                    )



                self.producto.stock -= diferencia



                tipo_movimiento = "SALIDA"



                cantidad_movimiento = diferencia




            elif diferencia < 0:



                self.producto.stock += abs(diferencia)



                tipo_movimiento = "ENTRADA"



                cantidad_movimiento = abs(diferencia)



            else:

                tipo_movimiento = None

                cantidad_movimiento = 0





            self.producto.save(
                update_fields=["stock"]
            )



            if tipo_movimiento:



                registrar_movimiento(

                    producto=self.producto,

                    tipo=tipo_movimiento,

                    cantidad=cantidad_movimiento,

                    stock_anterior=stock_anterior,

                    stock_nuevo=self.producto.stock,

                    usuario=self.salida.usuario,

                    referencia=self.salida.codigo

                )





        # ===========================
        # CALCULAR SUBTOTAL
        # ===========================


        self.subtotal = self.total_con_iva



        super().save(
            *args,
            **kwargs
        )



        self.salida.actualizar_total()





    @transaction.atomic
    def delete(self, *args, **kwargs):


        stock_anterior = self.producto.stock



        self.producto.stock += self.cantidad



        self.producto.save(
            update_fields=["stock"]
        )



        registrar_movimiento(

            producto=self.producto,

            tipo="ENTRADA",

            cantidad=self.cantidad,

            stock_anterior=stock_anterior,

            stock_nuevo=self.producto.stock,

            usuario=self.salida.usuario,

            referencia=self.salida.codigo

        )

        salida = self.salida

        result = super().delete(*args, **kwargs)
        salida.actualizar_total()
        return result




    def __str__(self):

        return (

            f"{self.salida.codigo} - "

            f"{self.producto.nombre}"

        )