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
    path('cleanup-request/edit/<int:id>/', editCleanupRequest, name='editCleanupRequest'),
    path('cleanup-request/delete/<int:id>/', deleteCleanupRequest, name='deleteCleanupRequest'),

    path('tasks/', getTasks, name='getTasks'),
    path('task/add/', addTask, name='addTask'),
    path('task/edit/<int:id>/', editTask, name='editTask'),
    path('task/delete/<int:id>/', deleteTask, name='deleteTask'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)