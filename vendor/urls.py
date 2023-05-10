from django.urls import path

from accounts.views import vendor_dashboard
from vendor.views import vendor_profile, catalog_builder

urlpatterns = [
    path('', vendor_dashboard, name='vendor'),
    path('profile/', vendor_profile, name='vendor_profile'),
    path('catalog-builder', catalog_builder, name='catalog_builder')
]
