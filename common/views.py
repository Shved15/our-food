from django.contrib.auth.mixins import UserPassesTestMixin

from accounts.views import check_role_customer, check_role_vendor


class CustomerUserPassesTestMixin(UserPassesTestMixin):

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_customer(self.request.user)


class VendorUserPassesTestMixin(UserPassesTestMixin):

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_vendor(self.request.user)
