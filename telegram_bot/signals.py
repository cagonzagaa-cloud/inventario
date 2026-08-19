from django.db.models.signals import post_save
from django.dispatch import receiver

from productos.models import Producto
from .models import Notificacion
from .services import crear_notificacion


@receiver(post_save, sender=Producto)
def alertar_stock_bajo(sender, instance, created, **kwargs):
    if not instance.estado or instance.stock > instance.stock_minimo:
        return
    mensaje = f"{instance.codigo} - {instance.nombre}: quedan {instance.stock} unidades (mínimo {instance.stock_minimo})."
    ultima = Notificacion.objects.filter(tipo=Notificacion.Tipo.STOCK, mensaje=mensaje).first()
    if ultima is None:
        crear_notificacion(Notificacion.Tipo.STOCK, "Alerta de stock bajo", mensaje, "/productos/")
