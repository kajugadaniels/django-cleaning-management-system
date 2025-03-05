from account.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Editable configuration for the custom User model
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {
            'fields': ('name', 'phone_number', 'nid', 'dob', 'profession', 'gender', 'image', 'address')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        # Remove auto-managed fields from the fieldsets and instead mark them as read-only.
        ('Important Dates', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'name', 'role', 'is_active', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('email',)
