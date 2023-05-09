from django.urls import path

from accounts.views import vendor_dashboard
from vendor.views import vendor_profile

urlpatterns = [
    path('', vendor_dashboard, name='vendor'),
    path('profile/', vendor_profile, name='vendor_profile')
]
