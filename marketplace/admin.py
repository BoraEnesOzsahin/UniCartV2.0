from django.contrib import admin
from .models import University, Profile, Category, Listing

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'is_seller')
    list_filter = ('is_seller', 'university')
    search_fields = ('user__username', 'university__name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'date')
    list_filter = ('categories', 'date')
    search_fields = ('title', 'description', 'seller__username')
    filter_horizontal = ('categories',)
    date_hierarchy = 'date'