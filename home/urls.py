from django.urls import path
from django.conf import settings
from home.views import *
from django.conf.urls.static import static

app_name = 'base'

urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('users/', getUsers, name='getUsers'),
    path('user/add', addUser, name='addUser'),
    path('user/edit/<int:id>/', editUser, name='editUser'),
    path('user/delete/<int:id>/', deleteUser, name='deleteUser'),

    path('cleanup-requests/', getCleanupRequests, name='getCleanupRequests'),
    path('cleanup-request/add/', addCleanupRequest, name='addCleanupRequest'),
    path('cleanup_requests/<int:cleanup_request_id>/', viewCleanupRequest, name='viewCleanupRequest'),

    path('admin/cleanup-requests/', adminViewCleanupRequests, name='adminViewCleanupRequests'),
    path('admin/cleanup-requests/<int:request_id>/', adminApproveCleanupRequest, name='adminApproveCleanupRequest'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)