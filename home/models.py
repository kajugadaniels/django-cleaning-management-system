import random
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
    invoice = models.FileField(upload_to='invoices/', null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    supervisor_report = models.FileField(upload_to='reports/', null=True, blank=True)

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

def invoice_file_path(instance, filename):
    random_number = random.randint(10000, 99999)
    client_name_slug = instance.client.name.replace(" ", "_").lower()
    return f'invoices/{client_name_slug}_{random_number}.pdf'

class Invoice(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Client'},
        related_name='invoices'
    )
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(
        upload_to=invoice_file_path,
        null=True,
        blank=True,
        help_text="Upload only PDF files"
    )
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-invoice_date']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return f"Invoice {self.id} - {self.client.email}"

def report_file_path(instance, filename):
    random_number = random.randint(10000, 99999)
    supervisor_name_slug = instance.supervisor.name.replace(" ", "_").lower()
    return f'invoices/{supervisor_name_slug}_{random_number}.pdf'

class WeeklyReport(models.Model):
    supervisor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Supervisor'},
        related_name='weeklyreports'
    )
    file = models.FileField(
        upload_to=report_file_path,
        null=True,
        blank=True,
        help_text="Upload only PDF files"
    )
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Weekly Reports'

    def __str__(self):
        return f"Invoice {self.id} - {self.supervisor.email}"