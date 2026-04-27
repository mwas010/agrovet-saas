"""
Luanda Feeds Centre - Agrovet Automation Software
WSGI config for production with Waitress.
"""

import os
from pathlib import Path
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luanda_feeds.settings')

BASE_DIR = Path(__file__).resolve().parent.parent
application = get_wsgi_application()
application = WhiteNoise(application, root=BASE_DIR / 'static')
