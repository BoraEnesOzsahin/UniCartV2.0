from django import forms
from .models import Listing


# ─────────────────────────────────────────
#  LISTING FORM
#  Used for both Create and Edit views
# ─────────────────────────────────────────
class ListingForm(forms.ModelForm):

    class Meta:
        model  = Listing
        fields = ['title', 'description', 'price', 'condition', 'category', 'image']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. MacBook Air M1 8GB',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the item — age, any damage, reason for selling…',
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'min': '0',
            }),
        }

    # ── Custom validation example ──
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters.")
        return title


# ─────────────────────────────────────────
#  SEARCH FORM  (optional — used in navbar)
# ─────────────────────────────────────────
class SearchForm(forms.Form):
    q        = forms.CharField(required=False, label='Search')
    category = forms.CharField(required=False)
