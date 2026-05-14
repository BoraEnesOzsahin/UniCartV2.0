"""Vercel Python entrypoint.

Vercel's Python runtime expects an `app.py` entrypoint.
We expose Django's WSGI application as `app`.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UniCart.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()

# Common aliases used by various WSGI/hosting conventions.
application = app
handler = app
