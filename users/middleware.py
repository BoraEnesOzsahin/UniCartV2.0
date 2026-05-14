from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from .models import UserProfile


class RequireEmailVerificationMiddleware:
    """Redirect authenticated users to settings until their email is verified."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        path = request.path

        exempt_paths = [
            '/users/login/',
            '/users/register/',
            '/users/logout/',
            '/users/settings/',
            '/users/verify-sent/',
            '/users/verify-success/',
        ]

        if path.startswith('/users/verify/'):
            return None

        if path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
            return None

        if path in exempt_paths:
            return None

        try:
            profile = request.user.userprofile
            if profile.email_verified:
                return None
        except UserProfile.DoesNotExist:
            pass

        messages.warning(request, 'Please verify your email before using UniCart.')
        return redirect('account_settings')
