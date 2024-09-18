from django.urls import path
from django.conf import settings
from home.views import *
from django.conf.urls.static import static

app_name = 'base'

urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('users/', getUsers, name='getUsers'),
    path('user/add', addUser, name='addUser'),

]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)