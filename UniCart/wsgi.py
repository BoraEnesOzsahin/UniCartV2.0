"""WSGI config for UniCart project.

This module exposes the WSGI callable for production deployments.
Vercel can use this file as an explicit entrypoint.
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniCart.settings')

application = get_wsgi_application()

# Common aliases used by some platforms/runtimes.
app = application
handler = application
