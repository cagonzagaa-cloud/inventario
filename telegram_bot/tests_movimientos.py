from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from categorias.models import Categoria
from clientes.models import Cliente
from entradas.models import Entrada
from productos.models import Producto
from proveedores.models import Proveedor
from reportes.models import MovimientoInventario
from salidas.models import Salida
from telegram_bot.services import registrar_entrada_desde_bot, registrar_salida_desde_bot


class MovimientosTelegramTest(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="admin_bot", password="clave-segura", is_active=True,
        )
        self.usuario.perfil.rol = "ADMIN"
        self.usuario.perfil.save(update_fields=["rol"])
        self.categoria = Categoria.objects.create(nombre="Telegram", descripcion="Pruebas")
        self.producto = Producto.objects.create(
            codigo="TG-001", nombre="Producto Telegram", categoria=self.categoria,
            costo=Decimal("10.00"), precio=Decimal("20.00"), stock=10, stock_minimo=1,
        )
        self.proveedor = Proveedor.objects.create(
            codigo="TG-PROV", tipo_identificacion="RUC", identificacion="1799999999001",
            razon_social="Proveedor Telegram", nombre_comercial="Proveedor Telegram",
            contacto="Admin", telefono="0999999999", correo="tg@example.com",
            direccion="Quito", provincia="Pichincha", canton="Quito", ciudad="Quito",
            condicion_pago="CONTADO", cupo_credito=0,
        )
        self.cliente = Cliente.objects.create(
            tipo_identificacion="CEDULA", identificacion="1712345678", nombres="Cliente",
            apellidos="Telegram", telefono="0999999998", correo="cliente@example.com",
        )

    def test_entrada_bot_se_registra_en_modulo_y_kardex(self):
        entrada, producto, stock_anterior = registrar_entrada_desde_bot(
            self.usuario.pk, self.proveedor.pk, self.producto.pk, 3, Decimal("10.00")
        )
        self.assertEqual(entrada.estado, "CONFIRMADA")
        self.assertEqual(stock_anterior, 10)
        self.assertEqual(producto.stock, 13)
        self.assertTrue(Entrada.objects.filter(pk=entrada.pk).exists())
        self.assertTrue(MovimientoInventario.objects.filter(
            referencia=entrada.codigo, tipo="ENTRADA", cantidad=3,
        ).exists())
        self.assertIn("Telegram", entrada.observaciones)

    def test_salida_bot_se_registra_en_modulo_y_kardex(self):
        salida = registrar_salida_desde_bot(
            self.usuario.pk, self.cliente.pk, self.producto.pk, 4
        )
        self.producto.refresh_from_db()
        self.assertEqual(salida.estado, "CONFIRMADA")
        self.assertEqual(self.producto.stock, 6)
        self.assertTrue(Salida.objects.filter(pk=salida.pk).exists())
        self.assertTrue(MovimientoInventario.objects.filter(
            referencia=salida.codigo, tipo="SALIDA", cantidad=4,
        ).exists())
        self.assertIn("Telegram", salida.observaciones)

    def test_usuario_no_administrador_no_puede_crear_movimientos_desde_bot(self):
        usuario = get_user_model().objects.create_user(
            username="usuario_bot", password="clave-segura", is_active=True,
        )
        with self.assertRaises(PermissionError):
            registrar_entrada_desde_bot(
                usuario.pk, self.proveedor.pk, self.producto.pk, 1, Decimal("10.00")
            )
