from django.urls import path
from marketplace.views import marketplace, vendor_detail

urlpatterns = [
    path('', marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', vendor_detail, name='vendor_detail'),
]
