from django import forms

from accounts.validators import allow_only_images_and_pdf_validator
from vendor.models import Vendor, OpeningHour


class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                     validators=[allow_only_images_and_pdf_validator])

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']


class OpeningHourForm(forms.ModelForm):
    """Form for create opening hours."""
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']
