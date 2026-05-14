"""WSGI config for UniCart project.

This module exposes the WSGI callable for production deployments.
Vercel can use this file as an explicit entrypoint.
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniCart.settings')

application = get_wsgi_application()


# Common aliases used by some platforms/runtimes.
app = application
handler = application
