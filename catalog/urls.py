from django.urls import path

from catalog.views import CategoryAddView, CategoryEditView, CategoryDeleteView, ProductAddView, ProductEditView, \
    product_delete

urlpatterns = [
    # category CRUD
    path('catalog-builder/category/add/', CategoryAddView.as_view(), name='category_add'),
    path('catalog-builder/category/edit/<int:pk>/', CategoryEditView.as_view(), name='category_edit'),
    path('catalog-builder/category/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category_delete'),

    # product item CRUD
    path('catalog-builder/product/add/', ProductAddView.as_view(), name='product_add'),
    path('catalog-builder/product/edit/<int:pk>/', ProductEditView.as_view(), name='product_edit'),
    path('catalog-builder/product/delete/<int:pk>/', product_delete, name='product_delete'),
]
