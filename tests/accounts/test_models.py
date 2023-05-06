from django.test import TestCase
from django.contrib.auth import get_user_model


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
