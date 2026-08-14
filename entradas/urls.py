from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.lista_entradas,
        name="lista_entradas"
    ),


    path(
        "crear/",
        views.crear_entrada,
        name="crear_entrada"
    ),


    path(
        "editar/<int:pk>/",
        views.editar_entrada,
        name="editar_entrada"
    ),


    path(
        "eliminar/<int:pk>/",
        views.eliminar_entrada,
        name="eliminar_entrada"
    ),


    path(
        "detalle/<int:pk>/",
        views.detalle_entrada,
        name="detalle_entrada"
    ),


    path(
        "detalle/<int:pk>/agregar/",
        views.agregar_detalle_entrada,
        name="agregar_detalle_entrada"
    ),


    path(
        "detalle/eliminar/<int:pk>/",
        views.eliminar_detalle_entrada,
        name="eliminar_detalle_entrada"
    ),


    path(
        "confirmar/<int:pk>/",
        views.confirmar_entrada,
        name="confirmar_entrada"
    ),

    path("detalle/editar/<int:pk>/",
    views.editar_detalle,
    name="editar_detalle"
),

]