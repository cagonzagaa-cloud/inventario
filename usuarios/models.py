from django.contrib.auth.models import User
from django.db import models


class PerfilUsuario(models.Model):
    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        USUARIO = "USUARIO", "Usuario"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.USUARIO,
    )

    @property
    def es_administrador(self):
        return self.rol == self.Rol.ADMIN

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"


User._meta.get_field("first_name")


def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)


models.signals.post_save.connect(
    crear_perfil_usuario,
    sender=User,
)
