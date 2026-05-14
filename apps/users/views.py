from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import RegisterForm, ProfileUpdateForm
from .models import UserProfile
from listings.models import Favorite


def _send_verification_email(request, user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    email_token = profile.generate_email_token()
    verification_url = request.build_absolute_uri(
        reverse('verify-email', args=[email_token])
    )
    subject = 'Verify your UniCart email'
    message = f"""
Hi {user.username},

Welcome to UniCart! Please verify your email by clicking the link below:

{verification_url}

This link will expire in 24 hours.

Best regards,
UniCart Team
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


# ─────────────────────────────────────────
#  REGISTER
#  New student signs up
#  URL: /users/register/
# ─────────────────────────────────────────
def register(request):
    if request.user.is_authenticated:
        return redirect('home')                # already logged in → go home

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create UserProfile and send verification email
            profile = UserProfile.objects.create(user=user)
            try:
                _send_verification_email(request, user)
                messages.info(request, 'Account created! Check your email to verify your account.')
                return redirect('email-verification-sent')
            except Exception as e:
                messages.error(request, f'Error sending verification email: {str(e)}')
                user.delete()
                return redirect('register')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def resend_verification(request):
    message_sent = False
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        if identifier:
            from django.contrib.auth.models import User
            try:
                if '@' in identifier:
                    user = User.objects.get(email__iexact=identifier)
                else:
                    user = User.objects.get(username__iexact=identifier)
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.email_verified = False
                profile.save()
                _send_verification_email(request, user)
                messages.success(request, 'Verification email resent. Check your inbox.')
                message_sent = True
            except Exception:
                # Do not expose whether the account exists
                messages.info(request, 'If an account exists, a verification email has been sent.')
                message_sent = True
        else:
            messages.error(request, 'Please enter your username or email.')

    return render(request, 'users/resend_verification.html', {
        'message_sent': message_sent,
    })


# ─────────────────────────────────────────
#  LOGIN
#  URL: /users/login/
# ─────────────────────────────────────────
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username, password=password)

        if user:
            # Check if email is verified
            try:
                profile = user.userprofile
                if not profile.email_verified:
                    messages.error(request, 'Please verify your email before logging in. You can resend a verification link.')
                    return redirect('resend_verification')
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
                try:
                    _send_verification_email(request, user)
                    messages.error(request, 'Your account is not verified. A verification email has been sent.')
                except Exception as e:
                    messages.error(request, f'Error sending verification email: {str(e)}')
                return redirect('resend_verification')

            login(request, user)
            return redirect(request.GET.get('next', 'home'))   # go to intended page or home
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


# ─────────────────────────────────────────
#  LOGOUT
#  URL: /users/logout/
# ─────────────────────────────────────────
@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─────────────────────────────────────────
#  EMAIL VERIFICATION SENT
#  Shows message that verification email was sent
#  URL: /users/verify-sent/
# ─────────────────────────────────────────
def email_verification_sent(request):
    return render(request, 'users/email_verification_sent.html')


# ─────────────────────────────────────────
#  VERIFY EMAIL
#  User clicks link in email to verify
#  URL: /users/verify/<token>/
# ─────────────────────────────────────────
def verify_email(request, token):
    try:
        profile = UserProfile.objects.get(email_token=token)
        
        # Check if token is not expired (24 hours)
        from django.utils import timezone
        from datetime import timedelta
        
        if profile.token_created_at:
            expiration_time = profile.token_created_at + timedelta(hours=24)
            if timezone.now() > expiration_time:
                messages.error(request, 'Verification link has expired. Please register again.')
                return redirect('register')
        
        # Verify email
        profile.verify_email()
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('email-verification-success')
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('register')


# ─────────────────────────────────────────
#  EMAIL VERIFICATION SUCCESS
#  Shows success message after email verification
#  URL: /users/verify-success/
# ─────────────────────────────────────────
def email_verification_success(request):
    return render(request, 'users/email_verification_success.html')


# ─────────────────────────────────────────
#  PROFILE  (public view — anyone can see)
#  Shows a user's active listings
#  URL: /users/<username>/
# ─────────────────────────────────────────
def profile(request, username):
    from django.contrib.auth.models import User
    user     = User.objects.get(username=username)  # TODO: handle 404
    listings = user.listings.filter(is_active=True, is_sold=False)
    favorited_listing_ids = set()
    if request.user.is_authenticated:
        favorited_listing_ids = set(
            Favorite.objects.filter(user=request.user, listing__in=listings)
            .values_list('listing_id', flat=True)
        )
    return render(request, 'users/profile.html', {
        'profile_user': user,
        'listings':     listings,
        'favorited_listing_ids': favorited_listing_ids,
    })


# ─────────────────────────────────────────
#  DASHBOARD  (private — only current user)
#  Shows own listings + favorites
#  URL: /users/dashboard/
# ─────────────────────────────────────────
@login_required
def dashboard(request):
    my_listings = request.user.listings.all()
    my_favorites = request.user.favorites.select_related('listing').all()
    favorited_listing_ids = set(
        request.user.favorites.values_list('listing_id', flat=True)
    )
    return render(request, 'users/dashboard.html', {
        'my_listings':  my_listings,
        'my_favorites': my_favorites,
        'favorited_listing_ids': favorited_listing_ids,
    })


# ─────────────────────────────────────────
#  SETTINGS  (private — only current user)
#  Basic account details update
#  URL: /users/settings/
# ─────────────────────────────────────────
@login_required
def account_settings(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile_form = ProfileUpdateForm(instance=profile, user=request.user)
    password_form = PasswordChangeForm(user=request.user)

    password_input_class = (
        'w-full px-4 py-3 border border-gray-200 rounded-xl outline-none '
        'focus:border-uni-orange focus:ring-2 focus:ring-orange-100 transition-all'
    )
    for field_name in ['old_password', 'new_password1', 'new_password2']:
        if field_name in password_form.fields:
            password_form.fields[field_name].widget.attrs.update({'class': password_input_class})

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            old_email = request.user.email
            profile_form = ProfileUpdateForm(request.POST, instance=profile, user=request.user)
            if profile_form.is_valid():
                profile = profile_form.save()
                user = profile.user
                if user.email != old_email:
                    profile.email_verified = False
                    profile.save()
                    try:
                        _send_verification_email(request, user)
                        messages.success(request, 'Settings saved. A new verification email has been sent.')
                    except Exception as e:
                        messages.error(request, f'Error sending verification email: {str(e)}')
                else:
                    messages.success(request, 'Settings saved.')
                return redirect('account_settings')

        if 'resend_verification' in request.POST:
            try:
                _send_verification_email(request, request.user)
                messages.success(request, 'Verification email resent. Check your inbox.')
            except Exception as e:
                messages.error(request, f'Error sending verification email: {str(e)}')
            return redirect('account_settings')

        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            for field_name in ['old_password', 'new_password1', 'new_password2']:
                if field_name in password_form.fields:
                    password_form.fields[field_name].widget.attrs.update({'class': password_input_class})

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated.')
                return redirect('account_settings')
            else:
                messages.error(request, 'Please correct the errors below.')

    email_verified = False
    try:
        email_verified = request.user.userprofile.email_verified
    except UserProfile.DoesNotExist:
        email_verified = False

    return render(request, 'users/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'email_verified': email_verified,
    })
