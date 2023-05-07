from django.urls import path
from accounts.views import register_user

urlpatterns = [
    path('register-user/', register_user, name='register_user')
]
