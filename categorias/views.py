from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.deletion import ProtectedError

from .models import Categoria
from .forms import CategoriaForm


@login_required
def lista_categorias(request):

    categorias = Categoria.objects.all().order_by("-id")

    form = CategoriaForm()

    contexto = {

        "categorias": categorias,

        "form": form

    }

    return render(request,
                "categorias/lista.html",contexto)


@login_required
def crear_categoria(request):

    if request.method == "POST":

        form = CategoriaForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Categoría creada correctamente.")

        else:

            messages.error(request, "Verifique los datos ingresados.")

    return redirect("lista_categorias")

@login_required
def editar_categoria(request, pk):

    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":

        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada correctamente.")
        else:
            messages.error(request, "Verifique los datos ingresados.")

    return redirect("lista_categorias")


@login_required
def eliminar_categoria(request, pk):

    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method != "POST":
        messages.warning(request, "Confirme la eliminación de la categoría desde el listado.")
        return redirect("lista_categorias")

    try:
        categoria.delete()
    except ProtectedError:
        messages.error(request, "No se puede eliminar la categoría porque tiene productos asociados.")
        return redirect("lista_categorias")

    messages.success(request, "Categoría eliminada correctamente.")

    return redirect("lista_categorias")

