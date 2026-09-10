from datetime import timedelta

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone

from .models import Profile, Membership


@receiver(post_save, sender=User)
def create_user_profile_and_membership(sender, instance, created, **kwargs):

    if created:

        Profile.objects.get_or_create(
            user=instance
        )

        now = timezone.now()

        Membership.objects.get_or_create(
            user=instance,
            defaults={
                "status": Membership.STATUS_TRIAL,
                "trial_started_at": now,
                "trial_ends_at": now + timedelta(days=7),
            },
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):

    if hasattr(instance, "profile"):
        instance.profile.save()
