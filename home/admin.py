from django.contrib import admin
from .models import CleanupRequest, Task

# Customize the CleanupRequest admin view
class CleanupRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'company', 'status', 'requested_at', 'approved_at', 'completed_at')
    list_filter = ('status', 'company', 'client', 'requested_at', 'approved_at', 'completed_at')
    search_fields = ('client__username', 'company__username', 'description')
    ordering = ('-requested_at',)

# Customize the Task admin view
class TaskAdmin(admin.ModelAdmin):
    list_display = ('cleanup_request', 'description', 'assigned_at', 'completed_at')
    list_filter = ('cleanup_request', 'assigned_at', 'completed_at')
    search_fields = ('description',)
    ordering = ('-assigned_at',)

# Register models in the admin site
admin.site.register(CleanupRequest, CleanupRequestAdmin)
admin.site.register(Task, TaskAdmin)
