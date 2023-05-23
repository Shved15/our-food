from django.urls import path

from accounts.views import CustomerDashboardView
from customer.views import customer_profile, my_orders, order_detail

urlpatterns = [
    path('', CustomerDashboardView.as_view(), name='customer'),
    path('profile/', customer_profile, name='customer_profile'),
    path('my-orders/', my_orders, name='customer_my_orders'),
    path('order-detail/<int:order_number>/', order_detail, name='customer_order_detail'),
]
