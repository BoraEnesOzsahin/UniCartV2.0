from django.urls import path
from . import views

# All URLs for the listings app
# Prefix: /listings/  (set in main unicart/urls.py)

urlpatterns = [
    path('',                  views.listing_list,   name='listing_list'),    # /listings/
    path('<int:pk>/',         views.listing_detail, name='listing_detail'),  # /listings/5/
    path('create/',           views.listing_create, name='listing_create'),  # /listings/create/
    path('<int:pk>/edit/',    views.listing_edit,   name='listing_edit'),    # /listings/5/edit/
    path('<int:pk>/delete/',  views.listing_delete, name='listing_delete'),  # /listings/5/delete/
]
