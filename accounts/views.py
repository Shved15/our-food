import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView

from accounts.forms import UserForm
from accounts.models import User, UserProfile
from accounts.utils import detect_user, send_verification_email
from orders.models import Order
from vendor.forms import VendorForm
from vendor.models import Vendor


# Restrict the vendor from accessing the customer page
def check_role_vendor(user) -> bool:
    """Check if the user has a vendor role."""
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the customer page
def check_role_customer(user) -> bool:
    """Check if the user has a customer role."""
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


class RegisterUserView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'accounts/register-user.html'
    success_url = reverse_lazy('register_user')

    def form_valid(self, form):
        """Handle form validation and save the new user."""
        if self.request.user.is_authenticated:
            messages.warning(self.request, 'You are already registered!')
            return redirect('my_account')

        user = form.save(commit=False)
        user.role = User.CUSTOMER
        user.save()

        # send verification email
        mail_subject = 'Please activate your account!'
        email_template = 'accounts/emails/account-verification-email.html'
        send_verification_email(self.request, user, mail_subject, email_template)

        messages.success(self.request, 'Your account has been registered successfully')
        return super().form_valid(form)


class RegisterVendorView(CreateView):
    """View for registering a vendor."""
    model = User
    form_class = UserForm
    template_name = 'accounts/register-vendor.html'
    success_url = reverse_lazy('register_vendor')

    def get_context_data(self, **kwargs):
        """Get the additional context data for the view."""
        context = super().get_context_data(**kwargs)
        context['vendor_form'] = VendorForm()
        return context

    def form_valid(self, form):
        """Handle form validation and save the new vendor."""
        if self.request.user.is_authenticated:
            # If the user is already authenticated,
            # display a warning message and redirect them to the 'my_account' page.
            messages.warning(self.request, 'You are already registered!')
            return redirect('my_account')

        # Create an instance of the VendorForm with the POST and FILES data.
        vendor_form = VendorForm(self.request.POST, self.request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            # Create the user manually using the cleaned form data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                            username=username, email=email, password=password)

            # Set the role of the user as 'VENDOR'
            user.role = User.VENDOR
            user.save()

            # Save the vendor form data with commit=False to prevent saving it immediately.
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor_name = vendor_form.cleaned_data['vendor_name']
            # Generate a vendor slug by slugging the vendor name and appending the user ID.
            vendor.vendor_slug = slugify(vendor_name) + '-' + str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # send verification email
            mail_subject = 'Please activate your account!'
            email_template = 'accounts/emails/account-verification-email.html'
            send_verification_email(self.request, user, mail_subject, email_template)

            messages.success(self.request,
                             'Your account has been registered successfully! Please wait for the approval.')
            return redirect('register_vendor')
        else:
            print('Invalid form')
            print(form.errors)
            print(vendor_form.errors)

        return super().form_valid(form)


def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated.')
        return redirect('my_account')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('my_account')


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('my_account')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('my_account')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')


@login_required(login_url='login')
def my_account(request):
    redirect_url = detect_user(user=request.user)
    return redirect(redirect_url)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/customer-dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders = orders[:10]

    # current month's revenue
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']

    # total revenue
    total_revenue = 0
    for order in orders:
        total_revenue += order.get_total_by_vendor()['grand_total']
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
    }
    return render(request, 'accounts/vendor-dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset-password-email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot-password.html')


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('my_account')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset-password.html')
