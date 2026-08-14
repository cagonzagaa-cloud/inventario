from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from categorias.models import Categoria
from clientes.models import Cliente
from productos.models import Producto
from .models import Salida, DetalleSalida


class DetalleSalidaTipoConversionTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
            password="12345678"
        )

        self.categoria = Categoria.objects.create(
            nombre="Categoría prueba",
            descripcion="Desc"
        )

        self.cliente = Cliente.objects.create(
            tipo_identificacion="CEDULA",
            identificacion="1712345678",
            nombres="Ana",
            apellidos="Pérez",
            telefono="0999999999",
            correo="ana@example.com",
            direccion="Quito",
        )

        self.producto = Producto.objects.create(
            codigo="P-001",
            nombre="Producto prueba",
            categoria=self.categoria,
            costo=Decimal("10.00"),
            precio=Decimal("12.50"),
            stock=10,
            stock_minimo=2,
        )

        self.salida = Salida.objects.create(
            cliente=self.cliente,
            fecha=date.today(),
            tipo="VENTA",
            usuario=self.user,
        )

    def test_save_casts_string_values_for_stock_and_subtotal(self):
        detalle = DetalleSalida(
            salida=self.salida,
            producto=self.producto,
            cantidad="3",
            precio="12.50",
        )

        detalle.save()

        self.producto.refresh_from_db()

        self.assertEqual(detalle.cantidad, 3)
        self.assertEqual(detalle.base, Decimal("37.50"))
        self.assertEqual(detalle.iva, Decimal("5.63"))
        self.assertEqual(detalle.total_con_iva, Decimal("43.13"))
        self.assertEqual(self.producto.stock, 7)
