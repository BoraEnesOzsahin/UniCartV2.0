from django.urls import path
from . import views

# All URLs for the listings app
# Prefix: /listings/  (set in main unicart/urls.py)

urlpatterns = [
    path('',                  views.listing_list,   name='listing_list'),    # /listings/
    path('category/<slug:slug>/', views.category_listings, name='category_listings'),  # /listings/category/tech/
    path('favorites/',        views.favorite_list,  name='favorite_list'),    # /listings/favorites/
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),  # /listings/5/favorite/
    path('<int:pk>/',         views.listing_detail, name='listing_detail'),  # /listings/5/
    path('create/',           views.listing_create, name='listing_create'),  # /listings/create/
    path('<int:pk>/edit/',    views.listing_edit,   name='listing_edit'),    # /listings/5/edit/
    path('<int:pk>/delete/',  views.listing_delete, name='listing_delete'),  # /listings/5/delete/
]
