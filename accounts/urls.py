from django.urls import path, include
from accounts.views import RegisterUserView, RegisterVendorView, UserLoginView, UserLogoutView,\
    CustomerDashboardView, VendorDashboardView, MyAccountView, ActivateAccountView, forgot_password,\
    reset_password_validate, reset_password

urlpatterns = [
    path('', MyAccountView.as_view()),

    path('register-user/', RegisterUserView.as_view(), name='register_user'),
    path('register-vendor/', RegisterVendorView.as_view(), name='register_vendor'),

    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('my-account/', MyAccountView.as_view(), name='my_account'),
    path('customer-dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('vendor-dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),

    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),

    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password-validate/<uidb64>/<token>/', reset_password_validate, name='reset_password_validate'),
    path('reset-password/', reset_password, name='reset_password'),

    path('vendor/', include('vendor.urls')),
    path('customer/', include('customer.urls')),
]
