from account.models import *
from django.db import models

class CleanupRequest(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Client'}, related_name='cleanup_requests')
    description = models.TextField()
    requested_date = models.DateTimeField(default=timezone.now)
    is_approved_by_admin = models.BooleanField(default=False)
    is_approved_by_company = models.BooleanField(default=False)
    assigned_company = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'Company'}, related_name='assigned_cleanups')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_cleanup_requests')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_cleanup_requests')
    deleteStatus = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cleanup Request by {self.client.name} on {self.requested_date}"

class Task(models.Model):
    cleanup_request = models.ForeignKey(CleanupRequest, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=255)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_tasks')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_tasks')
    deleteStatus = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task: {self.task_name} for Cleanup Request ID {self.cleanup_request.id}"