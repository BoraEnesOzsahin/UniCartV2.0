from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main pages
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    
    # Listing URLs
    path('listings/', views.listing_list, name='listing_list'),
    path('listings/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listings/create/', views.listing_create, name='listing_create'),
    path('listings/<int:pk>/edit/', views.listing_edit, name='listing_edit'),
    path('listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    
    # Support URLs
    path('support/', views.support, name='support'),
    path('faq/', views.faq, name='faq'),
]