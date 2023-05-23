from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from catalog.forms import CategoryForm, FoodItemForm
from catalog.models import Category, FoodItem
from common.views import VendorUserPassesTestMixin, check_role_vendor
from vendor.views import get_vendor


class CategoryAddView(LoginRequiredMixin, VendorUserPassesTestMixin, CreateView):
    """Class-based view to add a new category."""

    model = Category
    form_class = CategoryForm
    template_name = 'vendor/category-add.html'
    success_url = reverse_lazy('catalog_builder')
    login_url = 'login'

    def form_valid(self, form):
        """Save the category object after form validation."""
        category = form.save(commit=False)
        category.vendor = get_vendor(self.request)
        category.save()  # here the category id will be generated
        category.slug = slugify(category.category_name) + '-' + str(category.id)
        category.save()
        messages.success(self.request, 'Category added successfully!')
        return super().form_valid(form)


class CategoryEditView(LoginRequiredMixin, VendorUserPassesTestMixin, UpdateView):
    """Class-based view to edit an existing category."""

    model = Category
    form_class = CategoryForm
    template_name = 'vendor/category-edit.html'
    success_url = reverse_lazy('catalog_builder')
    login_url = 'login'

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


class CategoryDeleteView(LoginRequiredMixin, VendorUserPassesTestMixin, DeleteView):
    """Class-based view to delete an existing category."""

    model = Category
    success_url = reverse_lazy('catalog_builder')
    login_url = 'login'

    def delete(self, request, *args, **kwargs):
        """Delete the category and display success message."""
        category = self.get_object()
        category.delete()
        messages.success(request, 'Category has been deleted successfully!')
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        """Override the get method for using DeleteView without template_name."""
        return self.delete(request, *args, **kwargs)


class ProductAddView(LoginRequiredMixin, VendorUserPassesTestMixin, CreateView):
    """The view class to add the product."""

    model = FoodItem
    form_class = FoodItemForm
    template_name = 'vendor/product-add.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        """Override the get method to dynamically set the category field.
        The category field will be limited to only the categories associated with the current provider."""
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
        context = {'form': form}
        return render(request, self.template_name, context)

    def form_valid(self, form):
        """Called when the form is validly submitted."""
        food_title = form.cleaned_data['food_title']
        product = form.save(commit=False)
        product.vendor = get_vendor(self.request)
        product.save()
        product.slug = slugify(food_title) + '-' + str(product.id)  # generate unique slug for creating similar products
        form.save()
        messages.success(self.request, 'Product Item added successfully!')
        category_id = product.category.id
        return redirect(reverse('product_items_by_category', args=[category_id]))

    def form_invalid(self, form):
        """Called when the form is not validly submitted."""
        messages.error(self.request, 'Form validation failed')
        return super().form_invalid(form)


class ProductEditView(LoginRequiredMixin, VendorUserPassesTestMixin, UpdateView):
    """View for editing a product."""

    model = FoodItem
    form_class = FoodItemForm
    template_name = 'vendor/product-edit.html'
    context_object_name = 'product'
    login_url = 'login'

    def get_form_kwargs(self):
        # Override the method to pass an instance of the editable object to the form.
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def form_valid(self, form):
        # Overrides the method to save the changes to the object, set the required values,
        # and redirect after a successful save.
        food_title = form.cleaned_data['food_title']
        product = form.save(commit=False)
        product.vendor = get_vendor(self.request)
        product.slug = slugify(food_title)
        form.save()
        messages.success(self.request, 'Product Item updated successfully!')
        return redirect('product_items_by_category', product.category.id)

    def get_queryset(self):
        # Limit the selection to only objects owned by the current vendor.
        queryset = super().get_queryset()
        return queryset.filter(vendor=get_vendor(self.request))

    def get_context_data(self, **kwargs):
        # related form fields.
        context = super().get_context_data(**kwargs)
        context['form'].fields['category'].queryset = Category.objects.filter(vendor=get_vendor(self.request))
        return context


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def product_delete(request, pk=None):
    product = get_object_or_404(FoodItem, pk=pk)
    product.delete()
    messages.success(request, 'Product Item has been deleted successfully!')
    return redirect('product_items_by_category', product.category.id)
