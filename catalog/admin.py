from django.contrib import admin

from catalog.models import Category, FoodItem


admin.site.register(Category)
admin.site.register(FoodItem)
