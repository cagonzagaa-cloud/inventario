import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
    from django.conf import settings
    db = settings.DATABASES.get('default', {})
    print('ENGINE:', db.get('ENGINE'))
    print('HOST:', db.get('HOST'))
    print('NAME:', db.get('NAME'))
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)
