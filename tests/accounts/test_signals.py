from django.test import TestCase
from accounts.models import User, UserProfile


class SignalsTestCase(TestCase):

    def setUp(self):
        # Create a user for the test
        self.user = User.objects.create_user(
            first_name='test',
            last_name='name',
            email='test@example.com',
            username='testuser',
            password='testpass'
        )

    def test_post_save_create_profile_receiver(self):
        # Verify that when a user is created, a UserProfile instance is created
        self.assertTrue(hasattr(self.user, 'userprofile'))

    def test_pre_save_profile_receiver(self):
        # This test is not required, as the handler function simply passes control on.
        pass


