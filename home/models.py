from account.models import *
from django.db import models
from django.utils import timezone

class CleanupRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cleanup_requests')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cleanup_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    description = models.TextField()
    requested_at = models.CharField(max_length=40, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_added', null=True, blank=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_modified', null=True, blank=True)
    delete_status = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cleanup Request by {self.client}'

class Task(models.Model):
    cleanup_request = models.ForeignKey(CleanupRequest, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255, null=True, blank=True)
    cleaners = models.ManyToManyField(User, related_name='tasks_assigned', blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_added', null=True, blank=True)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_modified', null=True, blank=True)
    delete_status = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Task {self.name} for Request {self.cleanup_request}'
