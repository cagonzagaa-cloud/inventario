from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    name = 'usuarios'
    
    def ready(self):
        # Create a default SocialApp for Google in local development
        try:
            from django.conf import settings as _settings
            if not _settings.DEBUG:
                return

            from allauth.socialaccount.models import SocialApp
            from django.contrib.sites.models import Site
            import os

            provider = 'google'

            qs = SocialApp.objects.filter(provider=provider)

            if qs.exists():
                # If multiple entries exist, keep the first and delete the rest
                if qs.count() > 1:
                    first = qs.first()
                    qs.exclude(pk=first.pk).delete()
                app = qs.first()
            else:
                # create SocialApp with empty credentials (safe for local dev)
                site = Site.objects.get_current()
                app = SocialApp.objects.create(
                    provider=provider,
                    name='Google',
                    client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
                    secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
                )
                app.sites.add(site)

        except Exception:
            # Avoid breaking startup if any import or DB error occurs
            pass
