from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import PerfilUsuario


class RolUsuarioTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="usuario",
            password="12345678"
        )

        self.admin = get_user_model().objects.create_user(
            username="admin",
            password="12345678",
            is_staff=True,
        )

        self.user.perfil.rol = PerfilUsuario.Rol.USUARIO
        self.user.perfil.save(update_fields=["rol"])

        self.admin.perfil.rol = PerfilUsuario.Rol.ADMIN
        self.admin.perfil.save(update_fields=["rol"])

    def test_regular_user_is_not_system_admin(self):
        self.assertEqual(self.user.perfil.rol, PerfilUsuario.Rol.USUARIO)
        self.assertFalse(self.user.perfil.es_administrador)

    def test_regular_user_does_not_see_admin_menu(self):
        self.client.login(username="usuario", password="12345678")

        response = self.client.get(reverse("dashboard"))

        self.assertNotContains(response, "Usuarios")
        self.assertNotContains(response, "Configuración")

    def test_admin_user_can_see_admin_menu(self):
        self.client.login(username="admin", password="12345678")

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Usuarios")
        self.assertContains(response, "Configuración")

    def test_admin_can_access_user_management_page(self):
        self.client.login(username="admin", password="12345678")

        response = self.client.get(reverse("lista_usuarios"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuarios")

    def test_regular_user_cannot_access_admin_pages(self):
        self.client.login(username="usuario", password="12345678")

        response = self.client.get(reverse("lista_usuarios"))

        self.assertEqual(response.status_code, 302)

    def test_admin_can_access_configuration_page(self):
        self.client.login(username="admin", password="12345678")

        response = self.client.get(reverse("configuracion_sistema"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Configuración del sistema")

    def test_user_creation_requires_valid_password(self):
        self.client.login(username="admin", password="12345678")

        response = self.client.post(
            reverse("crear_usuario"),
            {
                "username": "nuevo_usuario",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "email": "nuevo@example.com",
                "password1": "123",
                "password2": "123",
                "rol": PerfilUsuario.Rol.USUARIO,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La contraseña debe tener al menos 6 caracteres.")
        self.assertFalse(get_user_model().objects.filter(username="nuevo_usuario").exists())

    def test_new_user_appears_in_table_after_creation(self):
        self.client.login(username="admin", password="12345678")

        response = self.client.post(
            reverse("crear_usuario"),
            {
                "username": "usuario_nuevo",
                "first_name": "Usuario",
                "last_name": "Nuevo",
                "email": "usuario_nuevo@example.com",
                "password1": "123456",
                "password2": "123456",
                "rol": PerfilUsuario.Rol.USUARIO,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "usuario_nuevo")
        self.assertTrue(get_user_model().objects.filter(username="usuario_nuevo").exists())

    def test_eliminar_usuario_lo_desactiva_y_conserva_el_registro(self):
        self.client.login(username="admin", password="12345678")
        response = self.client.post(reverse("eliminar_usuario", args=[self.user.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())

    def test_login_se_bloquea_despues_de_cinco_intentos_fallidos(self):
        self.client.logout()
        for intento in range(1, 6):
            response = self.client.post(reverse("login"), {
                "username": "usuario", "password": "incorrecta",
            })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "máximo de 5 intentos")
        response = self.client.post(reverse("login"), {
            "username": "usuario", "password": "12345678",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demasiados intentos fallidos")
