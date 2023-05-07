from django.urls import path
from accounts.views import register_user, register_vendor, login, logout, dashboard

urlpatterns = [
    path('register-user/', register_user, name='register_user'),
    path('register-vendor/', register_vendor, name='register_vendor'),

    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
]
