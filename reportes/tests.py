from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from categorias.models import Categoria
from productos.models import Producto
from .models import MovimientoInventario


class ExportarKardexExcelTest(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username="reporte", password="clave-segura")
        categoria = Categoria.objects.create(nombre="Reporte", descripcion="Prueba")
        self.producto = Producto.objects.create(
            codigo="REP-001", nombre="Producto reporte", categoria=categoria,
            costo=10, precio=15, stock=8, stock_minimo=1,
        )
        MovimientoInventario.objects.create(
            producto=self.producto, tipo="ENTRADA", cantidad=3,
            stock_anterior=5, stock_nuevo=8, usuario=self.usuario, referencia="ENT-TEST",
        )

    def test_exportacion_descarga_xlsx_con_movimientos(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse("exportar_kardex_excel"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment", respuesta["Content-Disposition"])
        libro = load_workbook(BytesIO(respuesta.content))
        hoja = libro["Kardex"]
        self.assertEqual(hoja["C2"].value, "REP-001")
        self.assertEqual(hoja["E2"].value, "Entrada")
        self.assertEqual(hoja["I2"].value, "ENT-TEST")
