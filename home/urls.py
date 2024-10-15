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

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)