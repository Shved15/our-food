from django import forms

from accounts.models import User


class UserForm(forms.ModelForm):
    """A form for creating a new user, with password confirmation."""
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    # def clean(self):
    #     """Custom form validation method to check if the password and confirm password fields match."""
    #     cleaned_data = super(UserForm, self).clean()
    #     password = cleaned_data.get('password')
    #     confirm_password = cleaned_data.get('confirm_password')
    #
    #     if password != confirm_password:
    #         raise forms.ValidationError(
    #             "Password does not match!"
    #         )

    class Meta:
        """ Model metadata for UserForm."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
