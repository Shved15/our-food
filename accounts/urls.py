from django.urls import path
from accounts.views import register_user, register_vendor, login, logout,\
    customer_dashboard, vendor_dashboard, my_account, activate

urlpatterns = [
    path('register-user/', register_user, name='register_user'),
    path('register-vendor/', register_vendor, name='register_vendor'),

    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    path('my-account/', my_account, name='my_account'),
    path('customer-dashboard/', customer_dashboard, name='customer_dashboard'),
    path('vendor-dashboard/', vendor_dashboard, name='vendor_dashboard'),

    path('activate/<uidb64>/<token>/', activate, name='activate'),
]
