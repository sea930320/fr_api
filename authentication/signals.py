# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from dataset.models import Dataset
#
# from .models import User

# @receiver(post_save, sender=User)
# def create_related_dataset(sender, instance, created, *args, **kwargs):
#     # Notice that we're checking for `created` here. We only want to do this
#     # the first time the `User` instance is created. If the save that caused
#     # this signal to be run was an update action, we know the user already
#     # has a profile.
#     if instance and created:
#         instance.dataset = Dataset.objects.create(user=instance)