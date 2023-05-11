from django.urls import path
from marketplace.views import marketplace, vendor_detail, add_to_cart

urlpatterns = [
    path('', marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', vendor_detail, name='vendor_detail'),

    # Add to Cart
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
]
