from django.urls import path

from .views import (
    LoginSistema,
    LogoutSistema,
    crear_usuario,
    editar_usuario,
    eliminar_usuario,
    lista_usuarios,
)

urlpatterns = [
    path("", LoginSistema.as_view(), name="login"),
    path("logout/", LogoutSistema.as_view(), name="logout"),
    path("usuarios/", lista_usuarios, name="lista_usuarios"),
    path("usuarios/crear/", crear_usuario, name="crear_usuario"),
    path("usuarios/<int:pk>/editar/", editar_usuario, name="editar_usuario"),
    path("usuarios/<int:pk>/eliminar/", eliminar_usuario, name="eliminar_usuario"),
]