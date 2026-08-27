from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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
        # Un borrador no altera el kardex; el movimiento ocurre al confirmar.
        self.assertEqual(self.producto.stock, 10)
        self.salida.confirmar(self.user)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)
        self.assertEqual(self.salida.estado, "CONFIRMADA")

    def test_formulario_unico_crea_detalle_confirma_y_descuenta_stock(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("crear_salida"), {
            "fecha": date.today().isoformat(), "cliente": self.cliente.pk,
            "tipo": "VENTA", "operacion_tributaria": "on",
            "detalles-TOTAL_FORMS": "1", "detalles-INITIAL_FORMS": "0",
            "detalles-MIN_NUM_FORMS": "1", "detalles-MAX_NUM_FORMS": "1000",
            "detalles-0-producto": self.producto.pk,
            "detalles-0-cantidad": "3", "detalles-0-precio": "12.50",
        })
        self.assertEqual(response.status_code, 302)
        nueva = Salida.objects.exclude(pk=self.salida.pk).get()
        self.assertEqual(nueva.estado, "CONFIRMADA")
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)

    def test_fecha_enviada_por_el_usuario_se_ignora(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("crear_salida"), {
            "fecha": "2020-01-01", "cliente": self.cliente.pk,
            "tipo": "VENTA", "operacion_tributaria": "on",
            "detalles-TOTAL_FORMS": "1", "detalles-INITIAL_FORMS": "0",
            "detalles-MIN_NUM_FORMS": "1", "detalles-MAX_NUM_FORMS": "1000",
            "detalles-0-producto": self.producto.pk,
            "detalles-0-cantidad": "1", "detalles-0-precio": "12.50",
        })

        self.assertEqual(response.status_code, 302)
        nueva = Salida.objects.exclude(pk=self.salida.pk).get()
        self.assertEqual(nueva.fecha, timezone.localdate())

    def test_formulario_inicia_con_una_fila_y_permite_agregar_mas(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("lista_salidas"))

        self.assertContains(response, 'name="detalles-TOTAL_FORMS" value="1"')
        self.assertContains(response, 'id="agregarFilaSalida"')
        self.assertContains(response, 'id="id_fecha"')
        self.assertContains(response, "required disabled")

    def test_eliminar_salida_confirmada_no_genera_error_500(self):
        Salida.objects.filter(pk=self.salida.pk).update(estado="CONFIRMADA")
        self.client.force_login(self.user)
        response = self.client.post(reverse("eliminar_salida", args=[self.salida.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Salida.objects.filter(pk=self.salida.pk).exists())
