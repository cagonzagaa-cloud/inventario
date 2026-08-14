from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.lista_categorias,
        name="lista_categorias"
    ),

    path(
        "nuevo/",
        views.crear_categoria,
        name="crear_categoria"
    ),

    path(
        "editar/<int:pk>/",
        views.editar_categoria,
        name="editar_categoria"
    ),

    path(
        "eliminar/<int:pk>/",
        views.eliminar_categoria,
        name="eliminar_categoria"
    ),

]