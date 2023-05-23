from django.urls import path

from accounts.views import CustomerDashboardView
from customer.views import CustomerProfileView, MyOrdersView, OrderDetailView

urlpatterns = [
    path('', CustomerDashboardView.as_view(), name='customer'),
    path('profile/', CustomerProfileView.as_view(), name='customer_profile'),
    path('my-orders/', MyOrdersView.as_view(), name='customer_my_orders'),
    path('order-detail/<int:order_number>/', OrderDetailView.as_view(), name='customer_order_detail'),
]
