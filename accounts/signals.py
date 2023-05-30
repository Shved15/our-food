from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from accounts.models import User, UserProfile


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    """Signal receiver function that gets triggered after a User model instance is saved.
     It creates a UserProfile instance associated with the saved user if it was just created,
     otherwise it updates the existing UserProfile instance."""
    print(created)
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except UserProfile.DoesNotExist:
            # Create the userprofile if not exist
            UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    """Signal receiver function that gets triggered before a User model instance is saved. It does nothing."""
    pass
