from .models import Notificacion


def notificaciones(request):
    perfil = getattr(request.user, "perfil", None) if request.user.is_authenticated else None
    es_admin = request.user.is_authenticated and (
        request.user.is_superuser or getattr(perfil, "es_administrador", False)
    )
    if not es_admin:
        return {"notificaciones_sistema": [], "notificaciones_pendientes": 0}
    queryset = Notificacion.objects.exclude(lecturas__usuario=request.user)
    return {
        "notificaciones_sistema": queryset[:8],
        "notificaciones_pendientes": queryset.count(),
    }
