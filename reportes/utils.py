from .models import MovimientoInventario


def registrar_movimiento(
    producto,
    tipo,
    cantidad,
    stock_anterior,
    stock_nuevo,
    usuario,
    referencia=None,
):

    MovimientoInventario.objects.create(

        producto=producto,

        tipo=tipo,

        cantidad=cantidad,

        stock_anterior=stock_anterior,

        stock_nuevo=stock_nuevo,

        usuario=usuario,

        referencia=referencia,

    )