from django.urls import path
from . import views

# All URLs for the users app
# Prefix: /users/  (set in main unicart/urls.py)

urlpatterns = [
    path('register/',         views.register,     name='register'),    # /users/register/
    path('login/',            views.user_login,   name='login'),       # /users/login/
    path('logout/',           views.user_logout,  name='logout'),      # /users/logout/
    path('dashboard/',        views.dashboard,    name='dashboard'),   # /users/dashboard/
    path('<str:username>/',   views.profile,      name='profile'),     # /users/enes/
]
