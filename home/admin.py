from home.models import *
from django.contrib import admin

class ReadOnlyAdmin(admin.ModelAdmin):
    """
    A base admin class that marks all model fields as read-only.
    Adding or deleting objects is disabled to maintain data integrity.
    """
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        # Include both standard and many-to-many fields
        readonly_fields = [field.name for field in self.model._meta.fields]
        readonly_fields += [field.name for field in self.model._meta.many_to_many]
        return readonly_fields

@admin.register(CleanupRequest)
class CleanupRequestAdmin(ReadOnlyAdmin):
    list_display = ('id', 'client', 'status', 'requested_at')

@admin.register(Task)
class TaskAdmin(ReadOnlyAdmin):
    list_display = ('id', 'cleanup_request', 'name', 'assigned_at', 'completed_at')

@admin.register(Invoice)
class InvoiceAdmin(ReadOnlyAdmin):
    list_display = ('id', 'client', 'invoice_date', 'due_date', 'amount', 'is_paid')

@admin.register(WeeklyReport)
class WeeklyReportAdmin(ReadOnlyAdmin):
    list_display = ('id', 'supervisor', 'created_at')
