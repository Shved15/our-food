from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView

from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from common.views import CustomerUserPassesTestMixin
from orders.models import Order, OrderedProduct

import simplejson as json


class CustomerProfileView(LoginRequiredMixin, CustomerUserPassesTestMixin, View):
    """Class-based view for customer profile."""

    template_name = 'customer/customer-profile.html'
    success_url = 'customer_profile'
    login_url = 'login'

    def get(self, request):
        """Handle GET requests."""
        profile = get_object_or_404(UserProfile, user=request.user)
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)
        context = {
            'profile_form': profile_form,
            'user_form': user_form,
            'profile': profile,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle POST requests."""
        profile = get_object_or_404(UserProfile, user=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            # Save the forms if they are valid
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated')
            return redirect(self.success_url)
        else:
            # Handle form validation errors
            print(profile_form.errors)
            print(user_form.errors)
            context = {
                'profile_form': profile_form,
                'user_form': user_form,
                'profile': profile,
            }
            return render(request, self.template_name, context)


class MyOrdersView(LoginRequiredMixin, CustomerUserPassesTestMixin, ListView):
    """
    Class-based view for displaying a list of user's orders.
    """
    template_name = 'customer/my-orders.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
    login_url = 'login'

    def get_queryset(self):
        """Get the queryset of orders for the authenticated user."""
        return Order.objects.filter(user=self.request.user, is_ordered=True)


class OrderDetailView(LoginRequiredMixin, CustomerUserPassesTestMixin, DetailView):
    """Class-based view for displaying the details of an order."""
    model = Order
    template_name = 'customer/order-detail.html'
    context_object_name = 'order'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        """Handle GET requests for the order detail view."""
        try:
            order = Order.objects.get(order_number=self.kwargs['order_number'], is_ordered=True)
            ordered_product = OrderedProduct.objects.filter(order=order)

            # Calculate the subtotal of the ordered products
            subtotal = sum(item.price * item.quantity for item in ordered_product)

            try:
                # Try to parse the tax data as JSON
                tax_data = json.loads(order.tax_data)
            except Exception as e:
                print(e)
                tax_data = order.tax_data
            context = {
                'order': order,
                'ordered_product': ordered_product,
                'subtotal': subtotal,
                'tax_data': tax_data,
            }
            return render(request, self.template_name, context)
        except Order.DoesNotExist:
            return redirect('customer')
