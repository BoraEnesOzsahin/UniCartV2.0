from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_verified', 'token_created_at')
    list_filter = ('email_verified', 'token_created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('email_token', 'token_created_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Verification', {
            'fields': ('email_verified', 'email_token', 'token_created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # UserProfile is created automatically during registration
