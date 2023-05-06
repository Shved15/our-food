from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User, UserProfile


class CustomUserAdmin(UserAdmin):
    """Custom admin view for the User model."""
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


# Register the User model with the CustomUserAdmin view
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
