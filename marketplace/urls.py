from django.urls import path
from marketplace.views import marketplace, vendor_detail, add_to_cart, decrease_cart, delete_cart

urlpatterns = [
    path('', marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', vendor_detail, name='vendor_detail'),

    # Add to Cart
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    # Decrease cart
    path('decrease-cart/<int:product_id>/', decrease_cart, name='decrease_cart'),
    # Delete Cart item
    path('delete-cart/<int:cart_id>/', delete_cart, name='delete_cart')


]
