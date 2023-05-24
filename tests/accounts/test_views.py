from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from accounts.forms import UserForm
from accounts.models import User
from vendor.forms import VendorForm
from vendor.models import Vendor


class RegisterUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register_user')

    def test_get_register_page(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register-user.html')

    def test_register_user(self):
        # Create a user data dictionary
        user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }

        response = self.client.post(self.register_url, data=user_data)

        # Check if the user is redirected to the registration page after successful registration.
        self.assertRedirects(response, self.register_url)

        # Check if the user is created in the database
        self.assertTrue(get_user_model().objects.filter(email='johndoe@example.com').exists())

    def test_register_user_invalid_form(self):
        # Create an invalid user data dictionary
        user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'password123',
            'confirm_password': 'different_password'
        }

        response = self.client.post(self.register_url, data=user_data)

        # Check if the user is not created in the database
        self.assertFalse(get_user_model().objects.filter(email='johndoe@example.com').exists())
        # Check if the registration page is rendered again with the form errors.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register-user.html')
        self.assertFormError(response, 'form', None, 'Password does not match!')


class RegisterVendorViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register_vendor')
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'test123',
            'confirm_password': 'test123'
        }
        self.vendor_data = {
            'vendor_name': 'Test Vendor',
            'vendor_license': SimpleUploadedFile("test_license.pdf", b"file_content", content_type="application/pdf")
        }

    def test_register_vendor_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register-vendor.html')
        self.assertIsInstance(response.context['form'], UserForm)
        self.assertIsInstance(response.context['vendor_form'], VendorForm)

    def test_register_vendor_post_valid_forms(self):
        response = self.client.post(self.register_url, data={**self.user_data, **self.vendor_data})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('register_vendor'))

        # Check if the user and vendor are created in the database.
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())
        self.assertTrue(Vendor.objects.filter(vendor_name=self.vendor_data['vendor_name']).exists())

    def test_register_vendor_post_invalid_forms(self):
        invalid_user_data = self.user_data.copy()
        invalid_user_data['email'] = 'invalid_email.com'  # Invalid email address
        invalid_vendor_data = self.vendor_data.copy()
        invalid_vendor_data['vendor_name'] = ''  # Empty vendor name

        response = self.client.post(self.register_url, data={**invalid_user_data, **invalid_vendor_data})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register-vendor.html')
        self.assertIsInstance(response.context['form'], UserForm)
        self.assertIsInstance(response.context['vendor_form'], VendorForm)
        self.assertTrue(response.context['form'].errors)
        self.assertTrue(response.context['vendor_form'].errors)


class UserLoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.my_account_url = reverse('my_account')
        self.user = User.objects.create_user(first_name='Joe',
                                             last_name='Doe',
                                             username='testuser',
                                             email='testuser@example.com',
                                             password='test123')

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')





