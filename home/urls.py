from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from home.views import (
    dashboard, getUsers, addUser, editUser, deleteUser,
    getCleanupRequests, addCleanupRequest, viewCleanupRequest, markCleanupRequestComplete,
    adminViewCleanupRequests, adminApproveCleanupRequest,
    viewManagerCleanupRequests, viewCleanupRequestDetails, assignCleanersToTask,
   
)

app_name = 'base'

urlpatterns = [
    path('', dashboard, name="dashboard"),
    
    path('users/', getUsers, name='getUsers'),
    path('user/add', addUser, name='addUser'),
    path('user/edit/<int:id>/', editUser, name='editUser'),
    path('user/delete/<int:id>/', deleteUser, name='deleteUser'),
    
    path('client/cleanup-requests/', getCleanupRequests, name='getCleanupRequests'),
    path('client/cleanup-request/add/', addCleanupRequest, name='addCleanupRequest'),
    path('client/cleanup-requests/<int:cleanup_request_id>/', viewCleanupRequest, name='viewCleanupRequest'),
    path('client/cleanup-request/<int:cleanupRequestId>/complete/', markCleanupRequestComplete, name='markCleanupRequestComplete'),
    
    path('cleanup-requests/', adminViewCleanupRequests, name='adminViewCleanupRequests'),
    path('cleanup-requests/<int:request_id>/', adminApproveCleanupRequest, name='adminApproveCleanupRequest'),
    
    path('manager/viewCleanupRequests/', viewManagerCleanupRequests, name='viewManagerCleanupRequests'),
    path('manager/cleanupRequests/<int:cleanupRequestId>/', viewCleanupRequestDetails, name='viewCleanupRequestDetails'),
    path('manager/assignCleaners/<int:taskId>/', assignCleanersToTask, name='assignCleanersToTask'),

   
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)