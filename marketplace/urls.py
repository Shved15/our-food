from django.urls import path
from marketplace.views import marketplace

urlpatterns = [
    path('', marketplace, name='marketplace'),
]
