from .models import UserProfile


def email_verification_status(request):
    email_verified = False
    if request.user.is_authenticated:
        try:
            email_verified = request.user.userprofile.email_verified
        except UserProfile.DoesNotExist:
            email_verified = False
    return {
        'email_verified': email_verified,
    }
