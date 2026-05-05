from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileUpdateForm


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
            login(request, user)               # log in immediately after signup
            messages.success(request, f'Welcome to UniCart, {user.username}!')
            return redirect('home')
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
