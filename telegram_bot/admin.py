from django.contrib import admin
from .models import Notificacion, NotificacionLeida, SuscripcionTelegram

admin.site.register(SuscripcionTelegram)
admin.site.register(Notificacion)
admin.site.register(NotificacionLeida)
