from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from home.views import *

app_name = 'base'

urlpatterns = [
    path('dashboard', dashboard, name="dashboard"),
    
    path('users/', getUsers, name='getUsers'),
    path('user/add', addUser, name='addUser'),
    path('user/edit/<int:id>/', editUser, name='editUser'),
    path('user/delete/<int:id>/', deleteUser, name='deleteUser'),
    
    path('cleanup-requests/', getCleanupRequests, name='getCleanupRequests'),
    path('cleanup-request/add/', addCleanupRequest, name='addCleanupRequest'),
    path('cleanup-request/<int:cleanup_request_id>/', viewCleanupRequest, name='viewCleanupRequest'),
    path('cleanup-requests/<int:request_id>/', adminApproveCleanupRequest, name='adminApproveCleanupRequest'),
    path('cleanup-requests/task/<int:taskId>/', assignCleanersToTask, name='assignCleanersToTask'),
    path('cleanup-request/<int:cleanup_request_id>/complete/', markCleanupRequestComplete, name='markCleanupRequestComplete'),
    path('cleanup-request/<int:cleanup_request_id>/submit_report/', submitSupervisorReport, name='submitSupervisorReport'),

    path('tasks/assigned/', getAssignedTasks, name='getAssignedTasks'),

    path('invoices/', getInvoices, name='getInvoices'),
    path('invoices/create/', createInvoice, name='createInvoice'),
    path('invoices/edit/<int:id>/', editInvoice, name='editInvoice'),
    path('invoices/delete/<int:id>/', deleteInvoice, name='deleteInvoice'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)