from django import forms

from accounts.models import User, UserProfile
from accounts.validators import allow_only_images_validator


class UserForm(forms.ModelForm):
    """A form for creating a new user, with password confirmation."""
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        """Custom form validation method to check if the password and confirm password fields match."""
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            # If the password and confirm password fields do not match, raise a validation error.
            raise forms.ValidationError(
                "Password does not match!"
            )

    class Meta:
        """ Model metadata for UserForm."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']


class UserProfileForm(forms.ModelForm):
    """UserProfile form, including images, address and other additional fields."""
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Start typing...', 'required': 'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                      validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),
                                  validators=[allow_only_images_validator])

    def __init__(self, *args, **kwargs):
        """Additional settings for the form fields are set, in this case,
        the latitude and longitude field is made readonly."""
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 'country',
                  'state', 'city', 'pin_code', 'latitude', 'longitude']


class UserInfoForm(forms.ModelForm):
    """Form for information about the user, including first name, last name and phone number."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
