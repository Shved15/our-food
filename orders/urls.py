from django.urls import path
from orders.views import place_order, payments, order_complete

urlpatterns = [
    path('place-order/', place_order, name='place_order'),
    path('payments/', payments, name='payments'),
    path('order-complete/', order_complete, name='order_complete'),
]
