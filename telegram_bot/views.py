from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings
from django.http import FileResponse, Http404
from pathlib import Path

from .models import Notificacion, NotificacionLeida


def qr_image(request):
    ruta = Path(settings.MEDIA_ROOT) / "telegram-qr.png"
    if not ruta.is_file():
        raise Http404("La imagen QR todavía no ha sido configurada.")
    return FileResponse(ruta.open("rb"), content_type="image/png")


@login_required
def marcar_leida(request, pk):
    notificacion = Notificacion.objects.get(pk=pk)
    NotificacionLeida.objects.get_or_create(notificacion=notificacion, usuario=request.user)
    return redirect(notificacion.url or "dashboard")


@login_required
def marcar_todas_leidas(request):
    NotificacionLeida.objects.bulk_create(
        [NotificacionLeida(notificacion=item, usuario=request.user) for item in Notificacion.objects.exclude(lecturas__usuario=request.user)],
        ignore_conflicts=True,
    )
    return redirect("dashboard")
