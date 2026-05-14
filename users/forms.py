from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# ─────────────────────────────────────────
#  REGISTER FORM
#  Extends Django's built-in UserCreationForm
#  Adds email field on top of username + password
# ─────────────────────────────────────────
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Use your university email')

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        # Optional: enforce university email domain
        # if not email.endswith('@youruniversity.edu.tr'):
        #     raise forms.ValidationError("Please use your university email.")
        return email


# ─────────────────────────────────────────
#  PROFILE UPDATE FORM
#  Let the user change their display info
# ─────────────────────────────────────────
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email']

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-uni-orange focus:ring-2 focus:ring-orange-100 transition-all',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-uni-orange focus:ring-2 focus:ring-orange-100 transition-all',
                'placeholder': 'Last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-uni-orange focus:ring-2 focus:ring-orange-100 transition-all',
                'placeholder': 'Email address',
            }),
        }
