from decimal import Decimal, ROUND_HALF_UP
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from .models import TarifaIVA, ClasificacionTributaria


def obtener_tarifa_vigente(porcentaje, fecha_operacion=None):
    fecha_operacion = fecha_operacion or date.today()
    tarifas = TarifaIVA.objects.filter(
        porcentaje=porcentaje,
        activo=True,
        fecha_inicio__lte=fecha_operacion,
    )
    tarifas = tarifas.filter(
        models.Q(fecha_fin__gte=fecha_operacion) | models.Q(fecha_fin__isnull=True)
    )
    return tarifas.order_by("fecha_inicio").first()


def obtener_tarifa_por_codigo(codigo, fecha_operacion=None):
    fecha_operacion = fecha_operacion or date.today()
    try:
        tarifa = TarifaIVA.objects.get(codigo=codigo, activo=True)
    except TarifaIVA.DoesNotExist:
        return None

    if tarifa.fecha_inicio > fecha_operacion:
        return None

    if tarifa.fecha_fin and tarifa.fecha_fin < fecha_operacion:
        return None

    return tarifa


def obtener_tarifa_general(fecha_operacion=None):
    fecha_operacion = fecha_operacion or date.today()
    tarifa = TarifaIVA.objects.filter(
        codigo="IVA_15",
        activo=True,
        fecha_inicio__lte=fecha_operacion,
    ).filter(
        models.Q(fecha_fin__gte=fecha_operacion) | models.Q(fecha_fin__isnull=True)
    ).first()
    if tarifa:
        return tarifa
    return TarifaIVA.objects.filter(
        porcentaje=Decimal("15.00"),
        activo=True,
        fecha_inicio__lte=fecha_operacion,
    ).filter(
        models.Q(fecha_fin__gte=fecha_operacion) | models.Q(fecha_fin__isnull=True)
    ).first()


def obtener_tarifa_producto(producto, fecha_operacion=None):
    fecha_operacion = fecha_operacion or date.today()

    if not producto.clasificacion_tributaria:
        return None

    tarifa = producto.clasificacion_tributaria.tarifa

    if not tarifa.activo:
        return None

    if tarifa.fecha_inicio > fecha_operacion:
        return None

    if tarifa.fecha_fin and tarifa.fecha_fin < fecha_operacion:
        return None

    return tarifa


def resolver_tarifa(producto, fecha_operacion=None, *, operacion_tributaria=True,
                    actividad=None, tiene_registro_turismo=False,
                    tiene_licencia_anual=False):
    """Resuelve la tarifa en servidor. Las excepciones requieren contexto explícito."""
    from .models import ReglaTemporalIVA

    fecha_operacion = fecha_operacion or date.today()
    if not operacion_tributaria:
        return None
    if actividad:
        reglas = ReglaTemporalIVA.objects.select_related("tarifa").filter(
            activo=True, actividad=actividad, fecha_inicio__lte=fecha_operacion,
            fecha_fin__gte=fecha_operacion, tarifa__activo=True,
        )
        for regla in reglas:
            if regla.requiere_registro_turismo and not tiene_registro_turismo:
                continue
            if regla.requiere_licencia_anual and not tiene_licencia_anual:
                continue
            return regla.tarifa
    return obtener_tarifa_producto(producto, fecha_operacion) or (
        obtener_tarifa_general(fecha_operacion) if not producto.clasificacion_tributaria_id else None
    )


def obtener_porcentaje_iva_producto(producto, fecha_operacion=None, fallback_general=True):
    fecha_operacion = fecha_operacion or date.today()

    if producto.clasificacion_tributaria:
        tarifa = obtener_tarifa_producto(producto, fecha_operacion)
        if tarifa:
            return tarifa.porcentaje
        return None

    if fallback_general:
        general = obtener_tarifa_general(fecha_operacion)
        if general:
            return general.porcentaje

    return None


def calcular_iva_detalle(cantidad, valor_unitario, porcentaje_tarifa):
    if porcentaje_tarifa is None:
        raise ValueError(
            "No se ha podido determinar la tarifa de IVA para el producto. "
            "Revise la clasificación tributaria y las tarifas vigentes."
        )

    cantidad = Decimal(str(cantidad))
    valor_unitario = Decimal(str(valor_unitario))
    porcentaje_tarifa = Decimal(str(porcentaje_tarifa))
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser mayor que cero.")
    if valor_unitario < 0:
        raise ValidationError("El valor unitario no puede ser negativo.")
    if porcentaje_tarifa < 0 or porcentaje_tarifa > 100:
        raise ValidationError("La tarifa de IVA debe estar entre 0 y 100.")
    subtotal = (cantidad * valor_unitario).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    iva = (subtotal * porcentaje_tarifa / Decimal("100.00")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    total = (subtotal + iva).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    return subtotal, iva, total


def obtener_desglose(detalles):
    """Agrupa bases e IVA por tarifa usando los valores históricos guardados."""
    desglose = {}
    subtotal_general = Decimal("0.00")
    iva_total = Decimal("0.00")
    for detalle in detalles:
        clave = str(detalle.porcentaje_iva.normalize())
        grupo = desglose.setdefault(clave, {"subtotal": Decimal("0.00"), "iva": Decimal("0.00")})
        grupo["subtotal"] += detalle.subtotal
        grupo["iva"] += detalle.valor_iva
        subtotal_general += detalle.subtotal
        iva_total += detalle.valor_iva
    return {"tarifas": desglose, "subtotal_general": subtotal_general,
            "iva_total": iva_total, "total": subtotal_general + iva_total}


def validar_clasificacion_tributaria(clasificacion_codigo):
    try:
        return ClasificacionTributaria.objects.get(codigo=clasificacion_codigo)
    except ClasificacionTributaria.DoesNotExist:
        raise ValidationError(
            f"Clasificación tributaria {clasificacion_codigo} no encontrada."
        )
