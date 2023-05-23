from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin, DetailView

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from catalog.models import Category, FoodItem
from common.views import VendorUserPassesTestMixin
from orders.models import Order, OrderedProduct
from vendor.forms import VendorForm, OpeningHourForm
from vendor.models import Vendor, OpeningHour


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


class VendorProfileView(LoginRequiredMixin, VendorUserPassesTestMixin, View):
    """Update vendor profile data."""

    template_name = 'vendor/vendor-profile.html'
    login_url = 'login'

    def get(self, request):
        """Handles the GET request for displaying the vendor profile form."""
        # Retrieves the user's profile and vendor objects.
        profile = get_object_or_404(UserProfile, user=request.user)
        vendor = get_object_or_404(Vendor, user=request.user)

        # Creates form instances for profile and vendor.
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

        context = {
            'profile_form': profile_form,
            'vendor_form': vendor_form,
            'profile': profile,
            'vendor': vendor,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        """Handles the POST request for updating the vendor profile information."""
        # Retrieves the user's profile and vendor objects.
        profile = get_object_or_404(UserProfile, user=request.user)
        vendor = get_object_or_404(Vendor, user=request.user)

        # Creates form instances for profile and vendor with the submitted data.
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            # Saves the profile and vendor forms if they are valid.
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
        else:
            messages.error(request, 'Failed to update vendor information.')

        return redirect('vendor_profile')


class CatalogBuilderView(LoginRequiredMixin, VendorUserPassesTestMixin, ListView):
    """Controller to display list of categories"""

    template_name = 'vendor/catalog-builder.html'
    context_object_name = 'categories'
    login_url = 'login'  # Specifies the URL to redirect the user to when not authenticated.

    def get_queryset(self):
        # Get a list of categories for the current provider
        vendor = get_vendor(self.request)
        return Category.objects.filter(vendor=vendor).order_by('created_at')


class ProductItemsByCategoryView(LoginRequiredMixin, VendorUserPassesTestMixin, ListView):
    """Class-based view to display product items by a category."""

    model = FoodItem
    template_name = 'vendor/product-items-by-category.html'
    context_object_name = 'product_items'

    def get_queryset(self):
        """Get the queryset of product items filtered by a vendor and category."""
        vendor = get_vendor(self.request)
        category = get_object_or_404(Category, pk=self.kwargs['pk'])
        queryset = super().get_queryset().filter(vendor=vendor, category=category)
        return queryset

    def get_context_data(self, **kwargs):
        """Get the context data to be passed to the template."""
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, pk=self.kwargs['pk'])
        context['category'] = category
        return context


class OpeningHoursView(TemplateView):
    """View for displaying opening hours of a vendor."""

    template_name = 'vendor/opening-hours.html'

    def get_context_data(self, **kwargs):
        """Add the form and opening hours to the context for creating new opening hours."""
        context = super().get_context_data(**kwargs)
        context['form'] = OpeningHourForm()
        context['opening_hours'] = OpeningHour.objects.filter(vendor=get_vendor(self.request))
        return context


class AddOpeningHoursView(View):
    """Class-based view for adding opening hours."""

    def post(self, request):
        """Handle POST request to add opening hours."""
        # Check if the user is authenticated.
        if request.user.is_authenticated:
            # Check if the request is an AJAX request.
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Retrieve the data from the POST request.
                day = request.POST.get('day')
                from_hour = request.POST.get('from_hour')
                to_hour = request.POST.get('to_hour')
                is_closed = request.POST.get('is_closed')

                try:
                    # Create a new OpeningHour object with the provided data.
                    hour = OpeningHour.objects.create(vendor=get_vendor(request),
                                                      day=day,
                                                      from_hour=from_hour,
                                                      to_hour=to_hour,
                                                      is_closed=is_closed)
                    if hour:
                        day = OpeningHour.objects.get(id=hour.id)
                        if day.is_closed:
                            # Prepare the JSON response for a closed day.
                            response = {'status': 'success',
                                        'id': hour.id,
                                        'day': day.get_day_display(),
                                        'is_closed': 'Closed'}
                        else:
                            # Prepare the JSON response for an open day.
                            response = {'status': 'success',
                                        'id': hour.id,
                                        'day': day.get_day_display(),
                                        'from_hour': hour.from_hour,
                                        'to_hour': hour.to_hour}
                    return JsonResponse(response)
                except IntegrityError:
                    # Handle the case when the opening hour already exists for the specified day.
                    response = {'status': 'failed', 'message': f'{from_hour}-{to_hour} already exists for this day!'}
                    return JsonResponse(response)
            else:
                # Return an HTTP response for invalid requests.
                return HttpResponse('Invalid request')


class RemoveOpeningHoursView(SingleObjectMixin, View):
    """View for deleting opening hours."""

    model = OpeningHour

    def delete(self, request, *args, **kwargs):
        """Handle DELETE request to remove opening hours."""
        if request.user.is_authenticated:
            # Check if the request is an AJAX request.
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Get the OpeningHour object to be deleted.
                hour = self.get_object()
                hour.delete()
                return JsonResponse({'status': 'success', 'id': kwargs['pk']})
            else:
                # Return an error response for invalid requests.
                return JsonResponse({'status': 'error', 'message': 'Invalid request'})
        else:
            # Return an error response if authentication is required.
            return JsonResponse({'status': 'error', 'message': 'Authentication required'})

    def get(self, request, *args, **kwargs):
        """Handle GET request by invoking to delete() method."""
        return self.delete(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        """Handle HTTP method not allowed."""
        return JsonResponse({'status': 'error', 'message': 'Method Not Allowed'}, status=405)


class OrderDetailView(LoginRequiredMixin, VendorUserPassesTestMixin, DetailView):
    """View for displaying order details to vendor."""

    template_name = 'vendor/order-detail.html'
    model = Order
    object = None

    def get_context_data(self, **kwargs):
        """Get additional context data for the order detail view."""
        context = super().get_context_data(**kwargs)
        order = self.object
        # Get the ordered products for the current vendor
        ordered_product = OrderedProduct.objects.filter(order=order, product_item__vendor=get_vendor(self.request))
        # Calculate the total by vendor
        total_by_vendor = order.get_total_by_vendor()

        context['ordered_product'] = ordered_product
        context['subtotal'] = total_by_vendor['subtotal']
        context['tax_data'] = total_by_vendor['tax_dict']
        context['grand_total'] = total_by_vendor['grand_total']

        return context

    def get(self, request, *args, **kwargs):
        """Handle GET request for the order detail view."""
        order_number = self.kwargs['order_number']
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            self.object = order
        except Order.DoesNotExist:
            return redirect('vendor')

        return self.render_to_response(self.get_context_data())


class MyOrdersView(LoginRequiredMixin, VendorUserPassesTestMixin, ListView):
    """View for displaying a list of orders for a vendor."""

    template_name = 'vendor/my-orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        """Get the queryset of orders for the current vendor."""
        vendor = Vendor.objects.get(user=self.request.user)
        orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
        return orders

    def get_context_data(self, **kwargs):
        """Get the additional context data to be passed to the template."""
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context
