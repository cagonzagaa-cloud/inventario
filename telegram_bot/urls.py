from django.urls import path
from . import views

urlpatterns = [
    path("qr/", views.qr_image, name="telegram_qr"),
    path("<int:pk>/leer/", views.marcar_leida, name="marcar_notificacion_leida"),
    path("leer-todas/", views.marcar_todas_leidas, name="marcar_todas_notificaciones"),
]
