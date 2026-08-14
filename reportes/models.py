from django.db import models
from django.contrib.auth.models import User

from productos.models import Producto



class MovimientoInventario(models.Model):


    TIPOS_MOVIMIENTO = [

        ("ENTRADA", "Entrada"),

        ("SALIDA", "Salida"),

        ("AJUSTE", "Ajuste"),

    ]


    producto = models.ForeignKey(

        Producto,

        on_delete=models.PROTECT,

        related_name="movimientos"

    )


    tipo = models.CharField(

        max_length=20,

        choices=TIPOS_MOVIMIENTO

    )


    cantidad = models.PositiveIntegerField()


    stock_anterior = models.PositiveIntegerField()


    stock_nuevo = models.PositiveIntegerField()



    usuario = models.ForeignKey(

        User,

        on_delete=models.PROTECT,

        related_name="movimientos_inventario"

    )


    fecha = models.DateTimeField(

        auto_now_add=True

    )



    referencia = models.CharField(

        max_length=50,

        blank=True,

        null=True

    )



    observacion = models.TextField(

        blank=True,

        null=True

    )



    class Meta:

        verbose_name = "Movimiento de Inventario"

        verbose_name_plural = "Movimientos de Inventario"

        ordering = [

            "-fecha"

        ]



    def __str__(self):

        return f"{self.tipo} - {self.producto.nombre}"

    def get_detail_url(self):
        """Return a URL to the related Entrada/Salida detail when possible.

        This method attempts to resolve `self.referencia` (which stores codigo like
        'ENT-00001' or 'SAL-00001') to the corresponding object's detail view.
        If no matching object is found, returns None.
        """
        from django.urls import reverse

        if not self.referencia:
            return None

        ref = str(self.referencia)

        try:
            # Try Entrada
            from entradas.models import Entrada
            entrada = Entrada.objects.filter(codigo=ref).first()
            if entrada:
                return reverse('detalle_entrada', args=[entrada.pk])
        except Exception:
            pass

        try:
            # Try Salida
            from salidas.models import Salida
            salida = Salida.objects.filter(codigo=ref).first()
            if salida:
                return reverse('detalle_salida', args=[salida.pk])
        except Exception:
            pass

        return None