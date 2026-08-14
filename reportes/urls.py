from django.urls import path

from . import views


urlpatterns = [

    path(
        "kardex/",
        views.kardex,
        name="kardex"
    ),
    path(
        "api/ultimos_movimientos/",
        views.api_ultimos_movimientos,
        name="api_ultimos_movimientos"
    ),

]