from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from CoreRoot.views import HomeView
from marketplace.views import CartListView, SearchView, CheckoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),

    path('', include('accounts.urls')),

    path('marketplace/', include('marketplace.urls')),

    # Catalog Builder
    path('catalog/', include('catalog.urls')),

    # Cart
    path('cart/', CartListView.as_view(), name='cart'),

    # Search
    path('search/', SearchView.as_view(), name='search'),

    # Checkout
    path('checkout', CheckoutView.as_view(), name='checkout'),

    # ORDERS
    path('orders/', include('orders.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
