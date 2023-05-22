from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, ListView, CreateView, DeleteView

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor
from catalog.forms import CategoryForm, FoodItemForm
from catalog.models import Category, FoodItem
from orders.models import Order, OrderedProduct
from vendor.forms import VendorForm, OpeningHourForm
from vendor.models import Vendor, OpeningHour


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


class VendorProfileView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Update vendor profile data."""

    template_name = 'vendor/vendor-profile.html'
    login_url = 'login'

    def test_func(self):
        # Checks if the user has the vendor role.
        return check_role_vendor(self.request.user)

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


class CatalogBuilderView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Controller to display list of categories"""

    template_name = 'vendor/catalog-builder.html'
    context_object_name = 'categories'
    login_url = 'login'  # Specifies the URL to redirect the user to when not authenticated.

    def test_func(self):
        # Checking the user's role
        return check_role_vendor(self.request.user)

    def get_queryset(self):
        # Get a list of categories for the current provider
        vendor = get_vendor(self.request)
        return Category.objects.filter(vendor=vendor).order_by('created_at')


class ProductItemsByCategoryView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Class-based view to display product items by a category."""

    model = FoodItem
    template_name = 'vendor/product-items-by-category.html'
    context_object_name = 'product_items'

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_vendor(self.request.user)

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


class CategoryAddView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Class-based view to add a new category."""

    model = Category
    form_class = CategoryForm
    template_name = 'vendor/category-add.html'
    success_url = reverse_lazy('catalog_builder')
    login_url = 'login'

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_vendor(self.request.user)

    def form_valid(self, form):
        """Save the category object after form validation."""
        category = form.save(commit=False)
        category.vendor = get_vendor(self.request)
        category.save()  # here the category id will be generated
        category.slug = slugify(category.category_name) + '-' + str(category.id)
        category.save()
        messages.success(self.request, 'Category added successfully!')
        return super().form_valid(form)


class CategoryEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Class-based view to edit an existing category."""

    model = Category
    form_class = CategoryForm
    template_name = 'vendor/category-edit.html'
    success_url = reverse_lazy('catalog_builder')
    login_url = 'login'

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_vendor(self.request.user)

    def form_valid(self, form):
        """Save the updated category object after form validation."""
        category = form.save(commit=False)
        category.vendor = get_vendor(self.request)
        category.slug = slugify(category.category_name)
        form.save()
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)

    def get_object(self, queryset=None):
        """Get the category object based on the pk parameter."""
        pk = self.kwargs.get('pk')
        return get_object_or_404(Category, pk=pk)


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Class-based view to delete an existing category."""

    model = Category
    success_url = reverse_lazy('catalog_builder')
    login_url = 'login'

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_vendor(self.request.user)

    def delete(self, request, *args, **kwargs):
        """Delete the category and display success message."""
        category = self.get_object()
        category.delete()
        messages.success(request, 'Category has been deleted successfully!')
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        """Override the get method for using DeleteView without template_name."""
        return self.delete(request, *args, **kwargs)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def product_add(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            product = form.save(commit=False)
            product.vendor = get_vendor(request)
            product.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Product Item added successfully!')
            return redirect('product_items_by_category', product.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/product-add.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def product_edit(request, pk=None):
    product = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            product = form.save(commit=False)
            product.vendor = get_vendor(request)
            product.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Product Item  updated successfully!')
            return redirect('product_items_by_category', product.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=product)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'vendor/product-edit.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def product_delete(request, pk=None):
    product = get_object_or_404(FoodItem, pk=pk)
    product.delete()
    messages.success(request, 'Product Item has been deleted successfully!')
    return redirect('product_items_by_category', product.category.id)


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening-hours.html', context)


def add_opening_hours(request):
    # handle the data and save them inside the database
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')

            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour,
                                                  to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(),
                                    'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(),
                                    'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour + '-' + to_hour + ' already exists for this day!'}
                return JsonResponse(response)
        else:
            return HttpResponse('Invalid request')


def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})


def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_product = OrderedProduct.objects.filter(order=order, product_item__vendor=get_vendor(request))

        context = {
            'order': order,
            'ordered_product': ordered_product,
            'subtotal': order.get_total_by_vendor()['subtotal'],
            'tax_data': order.get_total_by_vendor()['tax_dict'],
            'grand_total': order.get_total_by_vendor()['grand_total'],
        }
    except:
        return redirect('vendor')
    return render(request, 'vendor/order-detail.html', context)


def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'vendor/my-orders.html', context)
