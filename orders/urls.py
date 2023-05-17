from django.urls import path
from orders.views import place_order

urlpatterns = [
    path('place-order/', place_order, name='place_order'),
]
