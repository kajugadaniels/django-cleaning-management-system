from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

class CleanupRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'supervisor', 'status', 'requested_at', 'approved_at', 'completed_at')
    list_filter = ('status', 'supervisor', 'client', 'requested_at', 'approved_at', 'completed_at')
    search_fields = ('client__username', 'supervisor__username', 'description')
    ordering = ('-requested_at',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('cleanup_request', 'name', 'assigned_at', 'completed_at')
    list_filter = ('cleanup_request', 'assigned_at', 'completed_at')
    search_fields = ('name',)
    ordering = ('-assigned_at',)

# Register models in the admin site
admin.site.register(User, UserAdmin)
admin.site.register(CleanupRequest, CleanupRequestAdmin)
admin.site.register(Task, TaskAdmin)
