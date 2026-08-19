from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccesoBotTest(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username="usuario", password="clave-segura")
        self.admin = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="clave-segura"
        )

    def test_usuario_normal_no_ve_bot_y_no_accede_a_sus_rutas(self):
        self.client.force_login(self.usuario)
        pagina = self.client.get(reverse("dashboard"))
        self.assertNotContains(pagina, "telegramQrModal")
        respuesta = self.client.get(reverse("telegram_qr"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta.url)

    def test_admin_ve_el_acceso_al_bot(self):
        self.client.force_login(self.admin)
        pagina = self.client.get(reverse("dashboard"))
        self.assertContains(pagina, "telegramQrModal")


class ErroresFormularioTest(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username="operador", password="clave-segura")
        self.client.force_login(self.usuario)

    def test_entrada_invalida_conserva_formulario_y_muestra_errores(self):
        respuesta = self.client.post(reverse("crear_entrada"), {})
        self.assertEqual(respuesta.status_code, 400)
        self.assertContains(respuesta, "Revise la información ingresada", status_code=400)

    def test_salida_invalida_conserva_formulario_y_muestra_errores(self):
        respuesta = self.client.post(reverse("crear_salida"), {})
        self.assertEqual(respuesta.status_code, 400)
        self.assertContains(respuesta, "Revise la información ingresada", status_code=400)
