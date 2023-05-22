from django.urls import path, include
from accounts.views import RegisterUserView, RegisterVendorView, UserLoginView, UserLogoutView,\
    CustomerDashboardView, VendorDashboardView, MyAccountView, ActivateAccountView, ForgotPasswordView,\
    ResetPasswordValidateView, ResetPasswordView

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

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path(
        'reset-password-validate/<uidb64>/<token>/', ResetPasswordValidateView.as_view(), name='reset_password_validate'
    ),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    path('vendor/', include('vendor.urls')),
    path('customer/', include('customer.urls')),
]
