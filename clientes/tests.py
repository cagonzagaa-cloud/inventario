from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cliente


class EliminarClienteTest(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="admin_clientes",
            password="clave-segura-123",
        )
        self.client.force_login(self.usuario)
        self.cliente = Cliente.objects.create(
            identificacion="0999999999",
            nombres="Cliente",
            apellidos="Prueba",
        )
        self.url = reverse("eliminar_cliente", args=[self.cliente.pk])

    def test_get_no_elimina_ni_desactiva_cliente(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("lista_clientes"))
        self.cliente.refresh_from_db()
        self.assertTrue(self.cliente.estado)

    def test_post_desactiva_y_conserva_cliente(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("lista_clientes"))
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.estado)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())
