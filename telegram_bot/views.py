from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.conf import settings
from django.http import FileResponse, Http404
from pathlib import Path

from .models import Notificacion, NotificacionLeida


def es_administrador(user):
    return user.is_authenticated and (
        user.is_superuser
        or getattr(getattr(user, "perfil", None), "es_administrador", False)
    )


solo_administradores = user_passes_test(es_administrador, login_url="login")


@solo_administradores
def qr_image(request):
    ruta = Path(settings.MEDIA_ROOT) / "telegram-qr.png"
    if not ruta.is_file():
        raise Http404("La imagen QR todavía no ha sido configurada.")
    return FileResponse(ruta.open("rb"), content_type="image/png")


@solo_administradores
def marcar_leida(request, pk):
    notificacion = Notificacion.objects.get(pk=pk)
    NotificacionLeida.objects.get_or_create(notificacion=notificacion, usuario=request.user)
    return redirect(notificacion.url or "dashboard")


@solo_administradores
def marcar_todas_leidas(request):
    NotificacionLeida.objects.bulk_create(
        [NotificacionLeida(notificacion=item, usuario=request.user) for item in Notificacion.objects.exclude(lecturas__usuario=request.user)],
        ignore_conflicts=True,
    )
    return redirect("dashboard")
