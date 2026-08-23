from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from categorias.models import Categoria
from productos.models import Producto
from reportes.models import MovimientoInventario
from productos.forms import ProductoForm


class AccesoProductosTest(TestCase):
    def test_usuario_no_autenticado_es_redirigido_al_login_con_mensaje(self):
        response = self.client.get(reverse("lista_productos"), follow=True)

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("lista_productos")}',
        )
        self.assertContains(
            response,
            "Debe iniciar sesión primero para acceder a esta página.",
        )


class ProductoStockMinimoTest(TestCase):

    def test_producto_admite_ubicacion_codigo_de_barras_y_lote(self):
        categoria = Categoria.objects.create(nombre="Almacén", descripcion="Test")
        producto = Producto.objects.create(
            codigo="P-UBI-1",
            codigo_barras="7501234567890",
            lote="LOTE-2026-001",
            ubicacion="Bodega A / Pasillo 2",
            nombre="Producto ubicado",
            categoria=categoria,
        )

        self.assertEqual(producto.codigo_barras, "7501234567890")
        self.assertEqual(producto.lote, "LOTE-2026-001")
        self.assertEqual(producto.ubicacion, "Bodega A / Pasillo 2")

    def test_codigo_de_barras_no_se_repite(self):
        categoria = Categoria.objects.create(nombre="Códigos", descripcion="Test")
        Producto.objects.create(
            codigo="P-COD-1", codigo_barras="123456789", nombre="Primero", categoria=categoria
        )
        form = ProductoForm(data={
            "codigo": "P-COD-2", "codigo_barras": "123456789", "nombre": "Segundo",
            "categoria": categoria.pk, "clasificacion_tributaria": "", "costo": "0",
            "precio": "0", "stock": "0", "stock_minimo": "0", "estado": "on",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("codigo_barras", form.errors)

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

    def test_buscar_producto_por_codigo_de_barras_o_lote(self):
        categoria = Categoria.objects.create(nombre="Búsqueda", descripcion="Test")
        producto = Producto.objects.create(
            codigo="BUS-001", codigo_barras="9988776655", lote="LOTE-BUSCADO",
            ubicacion="Estante Z", nombre="Producto encontrable", categoria=categoria,
        )
        otro = Producto.objects.create(codigo="BUS-002", nombre="Producto diferente", categoria=categoria)
        usuario = get_user_model().objects.create_user(username="buscador", password="12345678")
        self.client.force_login(usuario)

        por_barra = self.client.get(reverse("lista_productos"), {"q": "9988776655"})
        self.assertContains(por_barra, producto.nombre)
        self.assertNotContains(por_barra, otro.nombre)

        por_lote = self.client.get(reverse("lista_productos"), {"q": "lote-buscado"})
        self.assertContains(por_lote, producto.nombre)
        self.assertContains(por_lote, "Estante Z")
