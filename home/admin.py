from django.contrib import admin
from .models import CleanupRequest, Task

class CleanupRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'manager', 'status', 'requested_at', 'approved_at', 'completed_at')
    list_filter = ('status', 'manager', 'client', 'requested_at', 'approved_at', 'completed_at')
    search_fields = ('client__username', 'manager__username', 'description')
    ordering = ('-requested_at',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('cleanup_request', 'name', 'assigned_at', 'completed_at')
    list_filter = ('cleanup_request', 'assigned_at', 'completed_at')
    search_fields = ('name',)
    ordering = ('-assigned_at',)

# Register models in the admin site
admin.site.register(CleanupRequest, CleanupRequestAdmin)
admin.site.register(Task, TaskAdmin)
