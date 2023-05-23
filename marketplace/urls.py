from django.urls import path
from marketplace.views import MarketplaceView, VendorDetailView, AddToCartView, DecreaseCartView, DeleteCartView

urlpatterns = [
    path('', MarketplaceView.as_view(), name='marketplace'),
    path('<slug:vendor_slug>/', VendorDetailView.as_view(), name='vendor_detail'),

    # Add to Cart
    path('add-to-cart/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    # Decrease cart
    path('decrease-cart/<int:product_id>/', DecreaseCartView.as_view(), name='decrease_cart'),
    # Delete Cart item
    path('delete-cart/<int:cart_id>/', DeleteCartView.as_view(), name='delete_cart'),
]
