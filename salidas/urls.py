from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.lista_salidas,
        name="lista_salidas"
    ),


    path(
        "crear/",
        views.crear_salida,
        name="crear_salida"
    ),


    path(
        "editar/<int:pk>/",
        views.editar_salida,
        name="editar_salida"
    ),


    path(
        "eliminar/<int:pk>/",
        views.eliminar_salida,
        name="eliminar_salida"
    ),


    path("anular/<int:pk>/", views.anular_salida, name="anular_salida"),

    path(
        "detalle/<int:pk>/",
        views.detalle_salida,
        name="detalle_salida"
    ),


    path(
        "detalle/<int:pk>/agregar/",
        views.agregar_detalle_salida,
        name="agregar_detalle_salida"
    ),


    path(
        "detalle/eliminar/<int:pk>/",
        views.eliminar_detalle_salida,
        name="eliminar_detalle_salida"
    ),


    path(
        "producto/<int:pk>/precio/",
        views.obtener_precio_producto,
        name="obtener_precio_producto"
    ),
    path("confirmar/<int:pk>/", views.confirmar_salida, name="confirmar_salida"),

]
