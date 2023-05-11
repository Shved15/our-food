from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from catalog.models import Category, FoodItem
from marketplace.models import Cart
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
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                product_item = FoodItem.objects.get(id=product_id)
                # Check if the user has already added that food to the cart.
                try:
                    check_cart = Cart.objects.get(user=request.user, product_item=product_item)
                    # Increase the cart quantity
                    check_cart.quantity += 1
                    check_cart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity'})
                except:
                    check_cart = Cart.objects.create(user=request.user, product_item=product_item, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the product to the cart'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
