import os

import requests
from django.db import transaction
from django.db.models import Q

from .models import Notificacion, SuscripcionTelegram


def enviar_telegram(texto):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return False

    enviado = False
    suscripciones = SuscripcionTelegram.objects.filter(activo=True).filter(
        Q(usuario__is_superuser=True) | Q(usuario__perfil__rol="ADMIN")
    ).distinct()
    for chat_id in suscripciones.values_list("chat_id", flat=True):
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": texto},
                timeout=5,
            )
            enviado = response.ok or enviado
        except requests.RequestException:
            continue
    return enviado


def crear_notificacion(tipo, titulo, mensaje, url=""):
    notificacion = Notificacion.objects.create(tipo=tipo, titulo=titulo, mensaje=mensaje, url=url)

    def enviar():
        if enviar_telegram(f"{titulo}\n\n{mensaje}"):
            Notificacion.objects.filter(pk=notificacion.pk).update(enviada_telegram=True)

    transaction.on_commit(enviar)
    return notificacion
