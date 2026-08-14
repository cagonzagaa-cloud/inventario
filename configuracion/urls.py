from django.urls import path

from .views import configuracion_sistema

urlpatterns = [
    path("", configuracion_sistema, name="configuracion_sistema"),
]
