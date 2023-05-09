from django.contrib import admin

from vendor.models import Vendor


class VendorAdmin(admin.ModelAdmin):
    """Custom admin interface for the Vendor model."""
    # The fields to display in the list view of vendors in the admin interface.
    list_display = ('user', 'vendor_name', 'is_approved', 'created_at')
    # The fields in the list display that should link to the edit form for the corresponding vendor.
    list_display_links = ('user', 'vendor_name')
    list_editable = ('is_approved',)


admin.site.register(Vendor, VendorAdmin)
