from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView

from accounts.models import UserProfile
from catalog.models import Category, FoodItem
from marketplace.context_processors import get_cart_counter, get_cart_amounts
from marketplace.models import Cart
from orders.forms import OrderForm
from vendor.models import Vendor, OpeningHour


class MarketplaceView(ListView):
    """View for displaying the marketplace listings."""

    template_name = 'marketplace/listings.html'
    context_object_name = 'vendors'

    def get_queryset(self):
        """Get the queryset of vendors. Filters vendors based on the 'is_approved' and 'user__is_active' fields."""
        queryset = Vendor.objects.filter(is_approved=True, user__is_active=True)
        return queryset

    def get_context_data(self, **kwargs):
        """Get the additional context data to be passed to the template.
        Adds the 'vendor_count' variable to the context, representing the count of vendors."""
        context = super().get_context_data(**kwargs)
        vendor_count = self.object_list.count()
        context['vendor_count'] = vendor_count
        return context


class VendorDetailView(DetailView):
    """View for displaying the details of a vendor."""

    model = Vendor
    template_name = 'marketplace/vendor-details.html'
    slug_field = 'vendor_slug'
    slug_url_kwarg = 'vendor_slug'
    context_object_name = 'vendor'

    def get_queryset(self):
        """Get the queryset of vendors."""
        queryset = super().get_queryset()
        return queryset.filter(is_approved=True, user__is_active=True)

    def get_context_data(self, **kwargs):
        """Get the additional context data to be passed to the template."""
        context = super().get_context_data(**kwargs)
        vendor = self.object

        # Retrieve categories with prefetch_related to optimize database queries.
        categories = Category.objects.filter(vendor=vendor).prefetch_related(
            Prefetch(
                'food_items',
                queryset=FoodItem.objects.filter(is_available=True)
            )
        )

        # Retrieve opening hours for the vendor and order them.
        opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')

        # Check current day's opening hours.
        today_date = date.today()
        today = today_date.isoweekday()

        current_opening_hours = opening_hours.filter(day=today)

        # Check if the user is authenticated and retrieve their cart items.
        if self.request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=self.request.user)
        else:
            cart_items = None

        # Add the variables to the context.
        context['categories'] = categories
        context['opening_hours'] = opening_hours
        context['current_opening_hours'] = current_opening_hours
        context['cart_items'] = cart_items

        return context


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
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity',
                                         'cart_counter': get_cart_counter(request),
                                         'qty': check_cart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    check_cart = Cart.objects.create(user=request.user, product_item=product_item, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the product to the cart',
                                         'cart_counter': get_cart_counter(request),
                                         'qty': check_cart.quantity, 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request, product_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                product_item = FoodItem.objects.get(id=product_id)
                # Check if the user has already added that food to the cart.
                try:
                    check_cart = Cart.objects.get(user=request.user, product_item=product_item)
                    if check_cart.quantity > 1:
                        # Decrease the cart quantity
                        check_cart.quantity -= 1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity = 0
                    return JsonResponse({'status': 'Success', 'message': 'Decreased the cart quantity',
                                         'cart_counter': get_cart_counter(request),
                                         'qty': check_cart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item has been deleted!',
                                         'cart_counter': get_cart_counter(request),
                                         'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart Item does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

    # get vendor ids that has the product item the user is looking for
    fetch_vendors_by_product_items = FoodItem.objects.filter(
        food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)

    vendors = Vendor.objects.filter(
        Q(id__in=fetch_vendors_by_product_items) | Q(vendor_name__icontains=keyword,
                                                     is_approved=True, user__is_active=True))

    if latitude and longitude and radius:
        pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
        vendors = Vendor.objects.filter(
            Q(id__in=fetch_vendors_by_product_items) | Q(vendor_name__icontains=keyword,
                                                         is_approved=True, user__is_active=True),
            user_profile__location__distance_lte=(pnt, D(km=radius))
        ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)

    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
        'source_location': address,
    }
    return render(request, 'marketplace/listings.html', context)


@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }

    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)
