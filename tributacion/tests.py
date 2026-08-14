from datetime import date
from decimal import Decimal

from django.test import TestCase

from productos.models import Producto
from tributacion.models import ClasificacionTributaria, TarifaIVA
from categorias.models import Categoria


class TributacionIntegrationTest(TestCase):

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Categoría prueba", descripcion="Desc")
        self.tarifa_15 = TarifaIVA.objects.get(codigo="IVA_15")
        self.tarifa_0 = TarifaIVA.objects.get(codigo="IVA_0")
        self.clasificacion_15 = ClasificacionTributaria.objects.get(codigo="ALIMENTOS_PROCESADOS_15")
        self.clasificacion_0 = ClasificacionTributaria.objects.get(codigo="BASICOS_0")

    def test_producto_con_clasificacion_15_aplica_iva_quince(self):
        producto = Producto.objects.create(
            codigo="P-IVA15",
            nombre="Jugo procesado",
            categoria=self.categoria,
            costo=Decimal("2.50"),
            precio=Decimal("3.00"),
            stock=10,
            stock_minimo=2,
            clasificacion_tributaria=self.clasificacion_15,
        )

        self.assertEqual(producto.tarifa_iva, self.tarifa_15.porcentaje)
        self.assertEqual(producto.tarifa_iva_codigo, self.tarifa_15.codigo)

    def test_producto_con_clasificacion_0_aplica_iva_cero(self):
        producto = Producto.objects.create(
            codigo="P-IVA0",
            nombre="Arroz natural",
            categoria=self.categoria,
            costo=Decimal("1.00"),
            precio=Decimal("1.20"),
            stock=20,
            stock_minimo=5,
            clasificacion_tributaria=self.clasificacion_0,
        )

        self.assertEqual(producto.tarifa_iva, self.tarifa_0.porcentaje)
        self.assertEqual(producto.tarifa_iva_codigo, self.tarifa_0.codigo)
