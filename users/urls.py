from django.urls import path
from . import views

# All URLs for the users app
# Prefix: /users/  (set in main unicart/urls.py)

urlpatterns = [
    path('register/',                       views.register,                 name='register'),              # /users/register/
    path('login/',                          views.user_login,               name='login'),                 # /users/login/
    path('logout/',                         views.user_logout,              name='logout'),                # /users/logout/
    path('dashboard/',                      views.dashboard,                name='dashboard'),             # /users/dashboard/
    path('verify-sent/',                    views.email_verification_sent,  name='email-verification-sent'),  # /users/verify-sent/
    path('verify/<str:token>/',             views.verify_email,             name='verify-email'),          # /users/verify/<token>/
    path('verify-success/',                 views.email_verification_success, name='email-verification-success'),  # /users/verify-success/
    path('<str:username>/',                 views.profile,                  name='profile'),               # /users/enes/
]
