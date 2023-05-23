from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import UpdateView

from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from accounts.views import check_role_customer
from orders.models import Order, OrderedProduct

import simplejson as json


class CustomerProfileView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Class-based view for customer profile."""

    login_url = 'login'
    template_name = 'customer/customer-profile.html'
    success_url = 'customer_profile'
    login_url = 'login'

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_customer(self.request.user)

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


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'customer/my-orders.html', context)


def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_product = OrderedProduct.objects.filter(order=order)
        subtotal = 0
        for item in ordered_product:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_product': ordered_product,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'customer/order-detail.html', context)
    except:
        return redirect('customer')
