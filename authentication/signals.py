from .models import User, Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            Profile.objects.create(user=instance,role = 2)
        else:
            Profile.objects.create(user=instance, join_date=date.today())
    instance.profile.save()