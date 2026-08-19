from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from categorias.models import Categoria
from entradas.models import Entrada, DetalleEntrada
from productos.models import Producto
from proveedores.models import Proveedor
from reportes.models import MovimientoInventario


class DetalleEntradaIvaTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
            password="12345678",
        )
        self.categoria = Categoria.objects.create(nombre="Categoría prueba", descripcion="Desc")
        self.proveedor = Proveedor.objects.create(
            codigo="PR-001",
            tipo_identificacion="RUC",
            identificacion="1799999999001",
            razon_social="Proveedor Demo",
            nombre_comercial="Proveedor Demo",
            contacto="Contacto",
            telefono="0999999999",
            correo="proveedor@example.com",
            direccion="Quito",
            provincia="Pichincha",
            canton="Quito",
            ciudad="Quito",
            condicion_pago="CONTADO",
            cupo_credito=Decimal("0.00"),
        )
        self.producto = Producto.objects.create(
            codigo="P-001",
            nombre="Producto prueba",
            categoria=self.categoria,
            costo=Decimal("10.00"),
            precio=Decimal("15.00"),
            stock=0,
            stock_minimo=2,
        )
        self.entrada = Entrada.objects.create(
            proveedor=self.proveedor,
            fecha=date.today(),
            tipo="COMPRA",
            usuario=self.user,
        )

    def test_detalle_entrada_calcula_base_iva_y_total(self):
        detalle = DetalleEntrada(
            entrada=self.entrada,
            producto=self.producto,
            cantidad=4,
            costo=Decimal("10.00"),
        )

        detalle.save()

        self.assertEqual(detalle.base, Decimal("40.00"))
        self.assertEqual(detalle.iva, Decimal("6.00"))
        self.assertEqual(detalle.total_con_iva, Decimal("46.00"))
        self.assertEqual(self.entrada.total, Decimal("46.00"))

    def test_confirmar_entrada_creates_inventory_movement(self):
        detalle = DetalleEntrada.objects.create(
            entrada=self.entrada,
            producto=self.producto,
            cantidad=4,
            costo=Decimal("10.00"),
        )

        # Authenticate client before confirming entrada
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("confirmar_entrada", args=[self.entrada.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        # Refresh producto from DB to assert updated stock
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 4)
        movimiento = MovimientoInventario.objects.filter(producto=self.producto, tipo="ENTRADA").first()
        self.assertIsNotNone(movimiento)
        self.assertEqual(movimiento.cantidad, 4)

    def test_formulario_unico_crea_detalle_confirma_y_actualiza_stock(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("crear_entrada"), {
            "fecha": date.today().isoformat(), "proveedor": self.proveedor.pk,
            "tipo": "COMPRA", "operacion_tributaria": "on",
            "detalles-TOTAL_FORMS": "1", "detalles-INITIAL_FORMS": "0",
            "detalles-MIN_NUM_FORMS": "1", "detalles-MAX_NUM_FORMS": "1000",
            "detalles-0-producto": self.producto.pk,
            "detalles-0-cantidad": "2", "detalles-0-costo": "10.00",
        })
        self.assertEqual(response.status_code, 302)
        nueva = Entrada.objects.exclude(pk=self.entrada.pk).get()
        self.assertEqual(nueva.estado, "CONFIRMADA")
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)

    def test_eliminar_entrada_confirmada_no_genera_error_500(self):
        self.entrada.estado = "CONFIRMADA"
        Entrada.objects.filter(pk=self.entrada.pk).update(estado="CONFIRMADA")
        self.client.force_login(self.user)
        response = self.client.get(reverse("eliminar_entrada", args=[self.entrada.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Entrada.objects.filter(pk=self.entrada.pk).exists())
