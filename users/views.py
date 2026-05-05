from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import RegisterForm, ProfileUpdateForm
from .models import UserProfile


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
            
            # Create UserProfile and generate verification token
            profile = UserProfile.objects.create(user=user)
            email_token = profile.generate_email_token()
            
            # Build verification link
            verification_url = request.build_absolute_uri(
                reverse('verify-email', args=[email_token])
            )
            
            # Send verification email
            subject = 'Verify your UniCart email'
            message = f"""
Hi {user.username},

Welcome to UniCart! Please verify your email by clicking the link below:

{verification_url}

This link will expire in 24 hours.

Best regards,
UniCart Team
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.info(request, 'Account created! Check your email to verify your account.')
                return redirect('email-verification-sent')
            except Exception as e:
                messages.error(request, f'Error sending verification email: {str(e)}')
                user.delete()
                return redirect('register')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


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
                    messages.error(request, 'Please verify your email before logging in.')
                    return redirect('users/login.html')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please register again.')
                return redirect('register')
            
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
    return render(request, 'users/profile.html', {
        'profile_user': user,
        'listings':     listings,
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
    return render(request, 'users/dashboard.html', {
        'my_listings':  my_listings,
        'my_favorites': my_favorites,
    })
