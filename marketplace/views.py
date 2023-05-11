from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from catalog.models import Category, FoodItem
from vendor.models import Vendor


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'food_items',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    context = {
        'vendor': vendor,
        'categories': categories,
    }
    return render(request, 'marketplace/vendor-details.html', context)


def add_to_cart(request, product_id):
    return HttpResponse(product_id)
