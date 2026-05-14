import uuid
from django.db import models
from django.contrib.auth.models import User

class University(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Universities"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True)
    is_seller = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=255, blank=True, null=True, unique=True)
    token_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def generate_email_token(self):
        """Generate a unique token for email verification"""
        self.email_token = str(uuid.uuid4())
        from django.utils import timezone
        self.token_created_at = timezone.now()
        self.save()
        return self.email_token

    def verify_email(self):
        """Mark email as verified"""
        self.email_verified = True
        self.email_token = None
        self.token_created_at = None
        self.save()
