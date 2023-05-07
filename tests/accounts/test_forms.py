from django.test import TestCase
from accounts.forms import UserForm


class UserFormTestCase(TestCase):

    def test_password_match(self):
        """ Test that passwords match. """
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'secret',
            'confirm_password': 'secret'
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """ Test that passwords do not match. """
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'secret',
            'confirm_password': 'not_secret'
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Password does not match!', form.errors['__all__'])