from django.contrib import admin
from .models import Listing, Category, Favorite

# Registers models so you can manage them at /admin/

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}   # auto-fills slug from name


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display   = ['title', 'seller', 'price', 'condition', 'is_sold', 'created_at']
    list_filter    = ['condition', 'is_sold', 'category']
    search_fields  = ['title', 'seller__username']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'saved_at']
