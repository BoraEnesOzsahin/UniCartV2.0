from django import forms
from django.core.exceptions import ValidationError


class ReportConversationForm(forms.Form):
    reason = forms.ChoiceField(choices=[
        ('spam', 'Spam / flooding'),
        ('abuse', 'Abusive / hateful language'),
        ('scam', 'Scam / phishing attempt'),
        ('other', 'Other'),
    ])
    details = forms.CharField(widget=forms.Textarea, required=False, max_length=2000)


class ImageUploadForm(forms.Form):
    image = forms.ImageField()

    def clean_image(self):
        image = self.cleaned_data['image']
        if image.size > 5 * 1024 * 1024:
            raise ValidationError('Image is too large (max 5MB).')
        content_type = getattr(image, 'content_type', '') or ''
        allowed = {'image/jpeg', 'image/png', 'image/webp'}
        if content_type and content_type not in allowed:
            raise ValidationError('Unsupported image type. Use JPG, PNG, or WEBP.')
        return image
