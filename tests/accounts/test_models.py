from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import UserProfile, User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='password123',
        )

    def test_create_user(self):
        """Test creating a new user"""
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.role, None)
        self.assertEqual(self.user.is_admin, False)
        self.assertEqual(self.user.is_staff, False)
        self.assertEqual(self.user.is_active, False)
        self.assertEqual(self.user.is_superadmin, False)
        self.assertTrue(self.user.check_password('password123'))

    def test_create_superuser(self):
        """Test creating a new superuser"""
        superuser = get_user_model().objects.create_superuser(
            email='superuser@example.com',
            username='superuser',
            first_name='Super',
            last_name='User',
            password='password123',
        )
        self.assertEqual(superuser.email, 'superuser@example.com')
        self.assertEqual(superuser.username, 'superuser')
        self.assertEqual(superuser.first_name, 'Super')
        self.assertEqual(superuser.last_name, 'User')
        self.assertEqual(superuser.role, None)
        self.assertEqual(superuser.is_admin, True)
        self.assertEqual(superuser.is_staff, True)
        self.assertEqual(superuser.is_active, True)
        self.assertEqual(superuser.is_superadmin, True)
        self.assertTrue(superuser.check_password('password123'))


class UserProfileTest(TestCase):
    """Test case for UserProfile model."""

    @classmethod
    def setUpTestData(cls):
        # Create a User object
        user = User.objects.create_user(
            first_name='Test',
            last_name='Name',
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )

        # Create a UserProfile object
        profile = UserProfile.objects.create(
            user=user,
            address_1='123 Main St',
            city='New York',
            state='NY',
            country='USA',
            pin_code='10001',
            latitude='40.7128',
            longitude='-74.0060'
        )

    def test_user_profile_string_representation(self):
        """Test the string representation of UserProfile object."""
        user_profile = UserProfile.objects.get(id=1)
        self.assertEqual(str(user_profile), 'testuser@example.com')

    def test_user_profile_fields(self):
        """Test UserProfile object fields."""
        user_profile = UserProfile.objects.get(id=1)

        # Test address fields
        self.assertEqual(user_profile.address_1, '123 Main St')
        self.assertEqual(user_profile.address_2, None)
        self.assertEqual(user_profile.city, 'New York')
        self.assertEqual(user_profile.state, 'NY')
        self.assertEqual(user_profile.country, 'USA')
        self.assertEqual(user_profile.pin_code, '10001')

        # Test location fields
        self.assertEqual
