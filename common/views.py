from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


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


class CustomerUserPassesTestMixin(UserPassesTestMixin):

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_customer(self.request.user)


class VendorUserPassesTestMixin(UserPassesTestMixin):

    def test_func(self):
        """Check if the user passes the test for vendor role."""
        return check_role_vendor(self.request.user)
