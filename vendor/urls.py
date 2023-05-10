from django.urls import path

from accounts.views import vendor_dashboard
from vendor.views import vendor_profile, catalog_builder, product_items_by_category,\
    category_add, category_edit, category_delete

urlpatterns = [
    path('', vendor_dashboard, name='vendor'),
    path('profile/', vendor_profile, name='vendor_profile'),
    path('catalog-builder/', catalog_builder, name='catalog_builder'),
    path('catalog-builder/category/<int:pk>/', product_items_by_category, name='product_items_by_category'),

    # category CRUD
    path('catalog-builder/category/add/', category_add, name='category_add'),
    path('catalog-builder/category/edit/<int:pk>/', category_edit, name='category_edit'),
    path('catalog-builder/category/delete/<int:pk>/', category_delete, name='category_delete'),
]
