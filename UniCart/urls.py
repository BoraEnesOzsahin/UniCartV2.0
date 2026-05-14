from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from listings import views as listing_views

# ─────────────────────────────────────────
#  MAIN URL CONFIG
#  This is the entry point — Django reads this
#  file first and routes to the right app
# ─────────────────────────────────────────

urlpatterns = [
    # Admin panel
    path('admin/',      admin.site.urls),

    # Home page (root URL)
    path('',            listing_views.home, name='home'),

    # Listings app  →  goes to listings/urls.py
    path('listings/',   include('listings.urls')),

    # Core app (support, faq)
    path('',            include('core.urls')),

    # Users app  →  goes to users/urls.py
    path('users/',      include('users.urls')),

    # Chats app
    path('chats/',      include('chats.urls')),
]

# Serve uploaded media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
