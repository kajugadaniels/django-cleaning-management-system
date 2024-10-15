from django.urls import path
from django.conf import settings
from account.views import *
from django.conf.urls.static import static

app_name = 'auth'

urlpatterns = [
    path('', user_login, name="login"),
    # path('logout/', user_logout, name='logout'),

    # path('profile/', userProfile, name='userProfile'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)