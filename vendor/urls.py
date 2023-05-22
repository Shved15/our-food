from django.urls import path, include

from accounts.views import VendorDashboardView
from vendor.views import VendorProfileView, CatalogBuilderView, ProductItemsByCategoryView, opening_hours, \
    add_opening_hours, remove_opening_hours, order_detail, my_orders

urlpatterns = [
    # Profile
    path('', VendorDashboardView.as_view(), name='vendor'),
    path('profile/', VendorProfileView.as_view(), name='vendor_profile'),

    # Catalog builder
    path('catalog-builder/', CatalogBuilderView.as_view(), name='catalog_builder'),
    path('catalog-builder/category/<int:pk>/', ProductItemsByCategoryView.as_view(), name='product_items_by_category'),

    # Opening hour CRUD
    path('opening-hours/', opening_hours, name='opening_hours'),
    path('opening-hours/add/', add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', remove_opening_hours, name='remove_opening_hours'),

    # Orders
    path('order-detail/<int:order_number>/', order_detail, name='vendor_order_detail'),
    path('my-orders/', my_orders, name='vendor_my_orders'),
]
