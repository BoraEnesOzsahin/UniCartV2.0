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


from .models import UserProfile, University

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-uni-orange focus:ring-2 focus:ring-orange-100 transition-all',
        'placeholder': 'First name',
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-uni-orange focus:ring-2 focus:ring-orange-100 transition-all',
        'placeholder': 'Last name',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-uni-orange focus:ring-2 focus:ring-orange-100 transition-all',
        'placeholder': 'Email address',
    }))

    class Meta:
        model = UserProfile
        fields = ['university', 'is_seller']
        widgets = {
            'university': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-uni-orange focus:ring-2 focus:ring-orange-100 transition-all',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile
