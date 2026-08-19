from django.db import models
from django.conf import settings


class SuscripcionTelegram(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram")
    chat_id = models.BigIntegerField(unique=True)
    activo = models.BooleanField(default=True)
    fecha_vinculacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.chat_id}"


class Notificacion(models.Model):
    class Tipo(models.TextChoices):
        STOCK = "STOCK", "Stock bajo"
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"
        SISTEMA = "SISTEMA", "Sistema"

    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.SISTEMA)
    titulo = models.CharField(max_length=120)
    mensaje = models.TextField()
    url = models.CharField(max_length=255, blank=True)
    creada = models.DateTimeField(auto_now_add=True)
    enviada_telegram = models.BooleanField(default=False)

    class Meta:
        ordering = ["-creada"]

    def __str__(self):
        return self.titulo


class NotificacionLeida(models.Model):
    notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE, related_name="lecturas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    leida = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["notificacion", "usuario"], name="notificacion_usuario_unica")]
