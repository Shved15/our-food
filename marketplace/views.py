from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, DetailView, FormView

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


class AddToCartView(View):
    """View for adding items to cart."""

    def get(self, request, product_id):
        """Handle GET request to increase the cart quantity."""
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

        # Check if the request is AJAX
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

        # Check if the food item exists
        try:
            # Check if the product item exists
            product_item = FoodItem.objects.get(id=product_id)
            # Check if the user has already added that food to the cart.
            try:
                # Check if the user has already added the food item to the cart.
                check_cart = Cart.objects.get(user=request.user, product_item=product_item)
                # Increase the cart quantity
                check_cart.quantity += 1
                check_cart.save()
                return JsonResponse({'status': 'Success',
                                     'message': 'Increased the cart quantity',
                                     'cart_counter': get_cart_counter(request),
                                     'qty': check_cart.quantity,
                                     'cart_amount': get_cart_amounts(request)})
            except Cart.DoesNotExist:
                # Create a new cart item
                check_cart = Cart.objects.create(user=request.user, product_item=product_item, quantity=1)
                return JsonResponse({'status': 'Success',
                                     'message': 'Added the product to the cart',
                                     'cart_counter': get_cart_counter(request),
                                     'qty': check_cart.quantity,
                                     'cart_amount': get_cart_amounts(request)})
        except FoodItem.DoesNotExist:
            return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})


class DecreaseCartView(View):
    """View to decrease the quantity of a product in the cart."""

    def get(self, request, product_id):
        """Handle GET request to decrease the cart quantity."""
        # Check if the user is not authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

        # Check if the request is not an AJAX request
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

        try:
            # Check if the product exists
            product_item = FoodItem.objects.get(id=product_id)
            try:
                # Check if the user has the product in the cart
                check_cart = Cart.objects.get(user=request.user, product_item=product_item)
                if check_cart.quantity > 1:
                    # Decrease the cart quantity if it is greater than 1
                    check_cart.quantity -= 1
                    check_cart.save()
                else:
                    # Remove the product from the cart if the quantity becomes 0.
                    check_cart.delete()
                    check_cart.quantity = 0
                return JsonResponse({'status': 'Success',
                                     'message': 'Decreased the cart quantity',
                                     'cart_counter': get_cart_counter(request),
                                     'qty': check_cart.quantity,
                                     'cart_amount': get_cart_amounts(request)})
            except Cart.DoesNotExist:
                # The user does not have the product in the cart
                return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
        except FoodItem.DoesNotExist:
            # The product does not exist
            return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})


class DeleteCartView(View):
    """View to delete a cart item."""

    def get(self, request, cart_id):
        """Handle GET request to delete the cart item."""
        # Check if the user is not authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

        # Check if the request is not an AJAX request
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

        try:
            # Check if the cart item exists
            cart_item = Cart.objects.get(user=request.user, id=cart_id)
            if cart_item:
                # Delete the cart item
                cart_item.delete()
                return JsonResponse({'status': 'Success',
                                     'message': 'Cart item has been deleted!',
                                     'cart_counter': get_cart_counter(request),
                                     'cart_amount': get_cart_amounts(request)})
        except Cart.DoesNotExist:
            # The cart item does not exist
            return JsonResponse({'status': 'Failed', 'message': 'Cart Item does not exist!'})


class CartListView(LoginRequiredMixin, ListView):
    """View to display the user's cart."""

    template_name = 'marketplace/cart.html'
    context_object_name = 'cart_items'
    login_url = 'login'

    def get_queryset(self):
        """Get the cart items for the current user."""
        return Cart.objects.filter(user=self.request.user).order_by('created_at')


class SearchView(ListView):
    """View to display search results based on user input."""

    template_name = 'marketplace/listings.html'
    context_object_name = 'vendors'

    def get_queryset(self):
        """Get the filtered vendors based on the search parameters."""
        # Check if the 'address' parameter is present in the request GET parameters.
        if not 'address' in self.request.GET:
            return Vendor.objects.none()  # Return an empty queryset if 'address' is not present
        else:
            # Retrieve the search parameters from the request GET parameters
            latitude = self.request.GET['lat']
            longitude = self.request.GET['lng']
            radius = self.request.GET['radius']
            keyword = self.request.GET['keyword']

        # Retrieve vendor IDs that have the product item the user is looking for.
        fetch_vendors_by_product_items = FoodItem.objects.filter(
            food_title__icontains=keyword, is_available=True
        ).values_list('vendor', flat=True)

        # Filter the vendors based on the search criteria
        queryset = Vendor.objects.filter(
            Q(id__in=fetch_vendors_by_product_items) | Q(
                vendor_name__icontains=keyword, is_approved=True, user__is_active=True
            )
        )

        # Apply additional filtering based on location if latitude, longitude and radius are provided.
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            queryset = queryset.filter(
                Q(id__in=fetch_vendors_by_product_items) | Q(
                    vendor_name__icontains=keyword, is_approved=True, user__is_active=True
                ),
                user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            # Add a 'kms' attribute to each vendor object representing the distance in kilometers.
            for vendor in queryset:
                vendor.kms = round(vendor.distance.km, 1)

        return queryset

    def get_context_data(self, **kwargs):
        # Get the default context data from the parent class
        context = super().get_context_data(**kwargs)
        # Add additional context data for the template
        context['vendor_count'] = self.get_queryset().count()
        context['source_location'] = self.request.GET.get('address', '')
        return context


class CheckoutView(LoginRequiredMixin, FormView):
    """View for checkout process."""

    template_name = 'marketplace/checkout.html'
    form_class = OrderForm
    login_url = 'login'

    def get_context_data(self, **kwargs):
        # Get the default context data from the parent class
        context = super().get_context_data(**kwargs)

        # Retrieve the cart items for the logged-in user
        cart_items = Cart.objects.filter(user=self.request.user).order_by('created_at')
        cart_count = cart_items.count()

        # If the cart is empty, redirect back to the marketplace
        if cart_count <= 0:
            return redirect('marketplace')

        # Retrieve user profile details
        user_profile = UserProfile.objects.get(user=self.request.user)

        # Set default values for the form fields
        default_values = {
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'phone': self.request.user.phone_number,
            'email': self.request.user.email,
            'address': user_profile.address,
            'country': user_profile.country,
            'state': user_profile.state,
            'city': user_profile.city,
            'pin_code': user_profile.pin_code,
        }

        # Set the initial values for the form
        form = self.get_form(self.form_class)
        form.initial = default_values

        # Add the form and cart items to the context
        context['form'] = form
        context['cart_items'] = cart_items

        return context
