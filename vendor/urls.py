from django.urls import path

from accounts.views import VendorDashboardView
from vendor.views import VendorProfileView, CatalogBuilderView, ProductItemsByCategoryView,\
    category_add, category_edit, category_delete, product_add, product_edit, product_delete, opening_hours, \
    add_opening_hours, remove_opening_hours, order_detail, my_orders

urlpatterns = [
    path('', VendorDashboardView.as_view(), name='vendor'),
    path('profile/', VendorProfileView.as_view(), name='vendor_profile'),
    path('catalog-builder/', CatalogBuilderView.as_view(), name='catalog_builder'),
    path('catalog-builder/category/<int:pk>/', ProductItemsByCategoryView.as_view(), name='product_items_by_category'),

    # category CRUD
    path('catalog-builder/category/add/', category_add, name='category_add'),
    path('catalog-builder/category/edit/<int:pk>/', category_edit, name='category_edit'),
    path('catalog-builder/category/delete/<int:pk>/', category_delete, name='category_delete'),

    # product item CRUD
    path('catalog-builder/product/add/', product_add, name='product_add'),
    path('catalog-builder/product/edit/<int:pk>/', product_edit, name='product_edit'),
    path('catalog-builder/product/delete/<int:pk>/', product_delete, name='product_delete'),

    # Opening hour CRUD
    path('opening-hours/', opening_hours, name='opening_hours'),
    path('opening-hours/add/', add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', remove_opening_hours, name='remove_opening_hours'),

    path('order-detail/<int:order_number>/', order_detail, name='vendor_order_detail'),
    path('my-orders/', my_orders, name='vendor_my_orders'),
]
