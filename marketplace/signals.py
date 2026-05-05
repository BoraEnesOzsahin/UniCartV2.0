from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, University

#Creates signals to automatically create profiles for new users

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Get the first university or create one if none exists
        default_university = University.objects.first()
        if not default_university:
            default_university = University.objects.create(name="Default University", location="Default Location")
        Profile.objects.create(user=instance, university=default_university)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        default_university = University.objects.first()
        Profile.objects.create(user=instance, university=default_university)
    instance.profile.save()