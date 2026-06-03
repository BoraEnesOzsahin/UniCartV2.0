from .models import UserProfile


def email_verification_status(request):
    email_verified = False
    if request.user.is_authenticated:
        email_verified = request.session.get('email_verified', False)
        if not email_verified:
            try:
                email_verified = request.user.userprofile.email_verified
                if email_verified:
                    request.session['email_verified'] = True
            except UserProfile.DoesNotExist:
                email_verified = False
    return {
        'email_verified': email_verified,
    }
