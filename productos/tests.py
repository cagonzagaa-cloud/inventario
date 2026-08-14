from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from categorias.models import Categoria
from productos.models import Producto
from reportes.models import MovimientoInventario


class ProductoStockMinimoTest(TestCase):

    def test_producto_esta_bajo_stock_cuando_stock_es_igual_o_inferior_al_minimo(self):
        categoria = Categoria.objects.create(nombre="Electrónica", descripcion="Test")
        producto = Producto.objects.create(
            codigo="P-100",
            nombre="Parlante",
            categoria=categoria,
            costo=Decimal("5.00"),
            precio=Decimal("12.00"),
            stock=2,
            stock_minimo=2,
        )

        self.assertTrue(producto.esta_bajo_stock)

        producto.stock = 3
        producto.save(update_fields=["stock"])

        self.assertFalse(producto.esta_bajo_stock)

    def test_crear_producto_generates_entry_movement(self):
        categoria = Categoria.objects.create(nombre="Limpieza", descripcion="Test")
        User = get_user_model()
        user = User.objects.create_user(username="admin", password="12345678")
        self.client.force_login(user)

        response = self.client.post(
            reverse("crear_producto"),
            {
                "codigo": "P-200",
                "nombre": "Jabón",
                "descripcion": "Jabón de manos",
                "categoria": categoria.pk,
                "clasificacion_tributaria": "",
                "costo": "2.50",
                "precio": "6.00",
                "stock": "15",
                "stock_minimo": "5",
                "estado": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        producto = Producto.objects.get(codigo="P-200")
        movimiento = MovimientoInventario.objects.filter(producto=producto).first()
        self.assertIsNotNone(movimiento)
        self.assertEqual(movimiento.tipo, "ENTRADA")
        self.assertEqual(movimiento.cantidad, 15)

    def test_product_form_is_rendered_before_table(self):
        User = get_user_model()
        user = User.objects.create_user(username="admin", password="12345678")
        self.client.force_login(user)
        response = self.client.get(reverse("lista_productos"))
        form_index = response.content.decode("utf-8").index("id=\"formProducto\"")
        table_index = response.content.decode("utf-8").index("id=\"tablaProductos\"")
        self.assertLess(form_index, table_index)
