from django.urls import path

from accounts.views import customer_dashboard
from customer.views import customer_profile

urlpatterns = [
    path('', customer_dashboard, name='customer'),
    path('profile/', customer_profile, name='customer_profile'),
]
