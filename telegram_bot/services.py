import os
from decimal import Decimal

import requests
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Notificacion, SuscripcionTelegram


def _validar_administrador(usuario):
    perfil = getattr(usuario, "perfil", None)
    if not (usuario.is_superuser or (perfil and perfil.es_administrador)):
        raise PermissionError("Solo un administrador puede registrar movimientos desde Telegram.")


def enviar_telegram(texto):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return False

    enviado = False
    suscripciones = SuscripcionTelegram.objects.filter(activo=True).filter(
        Q(usuario__is_superuser=True) | Q(usuario__perfil__rol="ADMIN")
    ).distinct()
    for chat_id in suscripciones.values_list("chat_id", flat=True):
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": texto},
                timeout=5,
            )
            enviado = response.ok or enviado
        except requests.RequestException:
            continue
    return enviado


def crear_notificacion(tipo, titulo, mensaje, url=""):
    notificacion = Notificacion.objects.create(tipo=tipo, titulo=titulo, mensaje=mensaje, url=url)

    def enviar():
        if enviar_telegram(f"{titulo}\n\n{mensaje}"):
            Notificacion.objects.filter(pk=notificacion.pk).update(enviada_telegram=True)

    transaction.on_commit(enviar)
    return notificacion


@transaction.atomic
def registrar_entrada_desde_bot(usuario_id, proveedor_id, producto_id, cantidad, costo):
    from django.contrib.auth import get_user_model
    from entradas.models import Entrada, DetalleEntrada
    from productos.models import Producto
    from proveedores.models import Proveedor

    usuario = get_user_model().objects.get(pk=usuario_id, is_active=True)
    _validar_administrador(usuario)
    proveedor = Proveedor.objects.get(pk=proveedor_id, estado=True)
    producto = Producto.objects.select_for_update().get(pk=producto_id, estado=True)
    cantidad, costo = int(cantidad), Decimal(str(costo))
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    if costo < 0:
        raise ValueError("El costo no puede ser negativo.")
    stock_anterior = producto.stock
    entrada = Entrada.objects.create(
        proveedor=proveedor, fecha=timezone.localdate(), tipo="COMPRA", usuario=usuario,
        observaciones="Registrada y confirmada desde el bot de Telegram.",
    )
    DetalleEntrada.objects.create(
        entrada=entrada, producto=producto, cantidad=cantidad, costo=costo,
    )
    entrada.confirmar(usuario)
    producto.refresh_from_db()
    entrada.refresh_from_db()
    return entrada, producto, stock_anterior


@transaction.atomic
def registrar_salida_desde_bot(usuario_id, cliente_id, producto_id, cantidad):
    from django.contrib.auth import get_user_model
    from clientes.models import Cliente
    from productos.models import Producto
    from salidas.models import Salida, DetalleSalida

    usuario = get_user_model().objects.get(pk=usuario_id, is_active=True)
    _validar_administrador(usuario)
    cliente = Cliente.objects.get(pk=cliente_id, estado=True)
    producto = Producto.objects.select_for_update().get(pk=producto_id, estado=True)
    cantidad = int(cantidad)
    if cantidad <= 0 or cantidad > producto.stock:
        raise ValueError(f"Cantidad inválida. Stock disponible: {producto.stock}.")
    salida = Salida.objects.create(
        cliente=cliente, fecha=timezone.localdate(), tipo="VENTA", usuario=usuario,
        observaciones="Registrada y confirmada desde el bot de Telegram.",
    )
    DetalleSalida.objects.create(
        salida=salida, producto=producto, cantidad=cantidad, precio=producto.precio,
    )
    salida.confirmar(usuario)
    salida.refresh_from_db()
    return salida
