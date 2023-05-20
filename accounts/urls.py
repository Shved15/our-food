from django.urls import path, include
from accounts.views import RegisterUserView, register_vendor, login, logout,\
    customer_dashboard, vendor_dashboard, my_account, activate, forgot_password,\
    reset_password_validate, reset_password

urlpatterns = [
    path('', my_account),

    path('register-user/', RegisterUserView.as_view(), name='register_user'),
    path('register-vendor/', register_vendor, name='register_vendor'),

    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    path('my-account/', my_account, name='my_account'),
    path('customer-dashboard/', customer_dashboard, name='customer_dashboard'),
    path('vendor-dashboard/', vendor_dashboard, name='vendor_dashboard'),

    path('activate/<uidb64>/<token>/', activate, name='activate'),

    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password-validate/<uidb64>/<token>/', reset_password_validate, name='reset_password_validate'),
    path('reset-password/', reset_password, name='reset_password'),

    path('vendor/', include('vendor.urls')),
    path('customer/', include('customer.urls')),
]
