import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import slugify
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView

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


class RegisterUserView(View):
    """View for registering a user."""

    def get(self, request):
        """Handles GET requests for user registration."""
        # If the user is already authenticated, a warning message is displayed,
        # and the user is redirected to their account page.
        if request.user.is_authenticated:
            messages.warning(request, 'You are already registered!')
            return redirect('my_account')
        else:
            form = UserForm()
            context = {'form': form}
            return render(request, 'accounts/register-user.html', context)

    def post(self, request):
        """Handles POST requests for user registration."""
        # If the submitted form is valid, a new user is created with the provided
        # information, and a verification email is sent.
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,
                                            password=password)
            user.role = User.CUSTOMER
            user.save()

            # send verification email
            mail_subject = 'Please activate your account!'
            email_template = 'accounts/emails/account-verification-email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been registered successfully')
            return redirect('register_user')
        else:
            print('Invalid form')
            print(form.errors)
            context = {'form': form}
            return render(request, 'accounts/register-user.html', context)


class RegisterVendorView(View):
    """View for registering a vendor."""

    def get(self, request):
        """Handles GET requests for vendor registration."""
        if request.user.is_authenticated:
            messages.warning(request, 'You are already registered!')
            return redirect('my_account')
        else:
            form = UserForm()
            vendor_form = VendorForm()
            context = {'form': form, 'vendor_form': vendor_form}
            return render(request, 'accounts/register-vendor.html', context)

    def post(self, request):
        """Handles POST requests for vendor registration.
        If both the user form and vendor form are valid,
        a new user is created with the provided information,
        and the vendor details are saved."""
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            # Create the user and save vendor data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )

            # Set the role of the user as a vendor
            user.role = User.VENDOR
            user.save()

            # Save the vendor details using VendorForm data
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor_name = vendor_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name) + '-' + str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification email
            mail_subject = 'Please activate your account!'
            email_template = 'accounts/emails/account-verification-email.html'
            send_verification_email(request, user, mail_subject, email_template)

            # Display success message and redirect to the vendor registration page
            messages.success(request, 'Your account has been registered successfully! Please wait for the approval.')
            return redirect('register_vendor')
        else:
            # Display error messages and render the vendor registration page with the forms.
            print('Invalid form')
            print(form.errors)
            context = {'form': form, 'vendor_form': vendor_form}
            return render(request, 'accounts/register-vendor.html', context)


class ActivateAccountView(SuccessMessageMixin, View):
    """Account activation view."""
    success_message = 'Congratulations! Your account is activated.'

    def get(self, request, uidb64, token):
        """Handles GET requests to activate a user account.
        This method decodes the uidb64 parameter to retrieve the user ID,
        and checks if the token is valid. If both conditions are met,
        the user's account is activated by setting is_active to True.
        Success or failure messages are displayed accordingly."""
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Activate the user's account
            user.is_active = True
            user.save()
            self.success_message = 'Congratulations! Your account is activated.'
        else:
            self.success_message = 'Invalid activation link'

        # Display success or failure message
        messages.success(request, self.success_message)
        # Redirect to the user's account page
        return redirect('my_account')


class UserLoginView(View):
    """View for user log in."""

    def get(self, request):
        """Display the login page."""
        if request.user.is_authenticated:
            # If the user is already authenticated, display a warning message
            # and redirect them to the 'my_account' page.
            messages.warning(request, 'You are already logged in!')
            return redirect('my_account')
        return render(request, 'accounts/login.html')

    def post(self, request):
        """Process the login form submission."""
        if request.user.is_authenticated:
            # If the user is already authenticated, display a warning message
            # and redirect them to the 'my_account' page.
            messages.warning(request, 'You are already logged in!')
            return redirect('my_account')

        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user using the provided email and password
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # If the authentication is successful, log in the user
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('my_account')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')


class UserLogoutView(SuccessMessageMixin, LogoutView):
    next_page = 'login'  # The URL the user will be redirected to after logging out.
    success_message = 'You are logged out.'

    def get_next_page(self):
        """Returns the URL to which the user will be redirected after logging out.
        This method overrides the parent class method to include a success message
        indicating that the user has been successfully logged out."""
        next_page = super().get_next_page()
        # Add a success message indicating successful logout
        messages.info(self.request, self.success_message)
        return next_page


class MyAccountView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        """Handles GET requests for the user's account page."""
        redirect_url = detect_user(user=request.user)
        return redirect(redirect_url)


class CustomerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/customer-dashboard.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        """Retrieves and prepares the context data for rendering the customer dashboard template."""
        context = super().get_context_data(**kwargs)
        # Retrieve orders for the current user
        orders = Order.objects.filter(user=self.request.user, is_ordered=True).order_by('-created_at')
        recent_orders = orders[:5]
        # Add the orders, orders count, and recent orders to the context.
        context['orders'] = orders
        context['orders_count'] = orders.count()
        context['recent_orders'] = recent_orders
        return context

    def test_func(self):
        # Checks if the current user has the role of a customer.
        return check_role_customer(self.request.user)


class VendorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/vendor-dashboard.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        """Retrieves and prepares the context data for rendering the vendor dashboard template.
        This method retrieves the vendor associated with the current user and retrieves the orders
        that are associated with the vendor. It also calculates the total revenue and current month's
        revenue for the vendor. The orders and revenue data are added to the context."""
        context = super().get_context_data(**kwargs)
        # Retrieve the vendor for the current user
        vendor = Vendor.objects.get(user=self.request.user)
        # Retrieve orders for the vendor
        orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
        recent_orders = orders[:10]

        # Calculate a current month's revenue for the vendor
        current_month = datetime.datetime.now().month
        current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
        current_month_revenue = sum(order.get_total_by_vendor()['grand_total'] for order in current_month_orders)

        # Calculate total revenue for the vendor
        total_revenue = sum(order.get_total_by_vendor()['grand_total'] for order in orders)

        # Add data to the context
        context['orders'] = orders
        context['orders_count'] = orders.count()
        context['recent_orders'] = recent_orders
        context['total_revenue'] = total_revenue
        context['current_month_revenue'] = current_month_revenue
        return context

    def test_func(self):
        # Checks if the current user has the role of a vendor.
        return check_role_vendor(self.request.user)


class ForgotPasswordView(View):
    """View for handling password reset request."""

    def get(self, request):
        """Display the forgot password page."""
        return render(request, 'accounts/forgot-password.html')

    def post(self, request):
        """Process the password reset request."""
        email = request.POST.get('email')

        if email:
            # Check if account exists
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)

                # Send reset password email
                mail_subject = 'Reset Your Password'
                email_template = 'accounts/emails/reset-password-email.html'
                send_verification_email(request, user, mail_subject, email_template)

                messages.success(request, 'Password reset link has been sent to your email address.')
                return redirect('login')

        messages.error(request, 'Account does not exist')
        return redirect('forgot_password')


class ResetPasswordValidateView(View):
    """View for validating the reset password link and setting the session data for password reset."""

    def get(self, request, uidb64, token):
        """Handle GET request and validate the reset password link."""
        # Validate the user by decoding the token and user pk
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid
            messages.info(request, 'Please reset your password')
            return redirect('reset_password')
        else:
            messages.error(request, 'This link has expired!')
            return redirect('my_account')


class ResetPasswordView(View):
    """Reset password view."""
    def get(self, request):
        """Handles GET requests for the password reset view."""
        return render(request, 'accounts/reset-password.html')

    def post(self, request):
        """Handles POST requests for the password reset view.
        This method retrieves the new password and confirm a password from the form data. It compares the passwords
        and if they match, it retrieves the user from the session and updates the user's password. Finally, it
        redirects the user to the login page."""
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check if passwords match
        if password == confirm_password:
            # Retrieve user from session
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)

            # Update user's password
            user.set_password(password)
            user.is_active = True
            user.save()

            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('reset_password')
