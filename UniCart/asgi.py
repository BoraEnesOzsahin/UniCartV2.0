"""
ASGI config for UniCart project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path

# Ensure Django settings are set before importing any Django apps
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniCart.settings')

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'apps'))

# Initialize Django ASGI application first (this sets up app registry)
django_asgi_app = get_asgi_application()

# Now import routing that depends on app models
import chats.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chats.routing.websocket_urlpatterns
        )
    ),
})
