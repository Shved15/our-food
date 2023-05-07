from django.urls import path
from accounts.views import register_user, register_vendor

urlpatterns = [
    path('register-user/', register_user, name='register_user'),
    path('register-vendor/', register_vendor, name='register_vendor'),
]
