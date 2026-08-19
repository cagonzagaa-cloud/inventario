from .models import Notificacion


def notificaciones(request):
    if not request.user.is_authenticated:
        return {"notificaciones_sistema": [], "notificaciones_pendientes": 0}
    queryset = Notificacion.objects.exclude(lecturas__usuario=request.user)
    return {
        "notificaciones_sistema": queryset[:8],
        "notificaciones_pendientes": queryset.count(),
    }
