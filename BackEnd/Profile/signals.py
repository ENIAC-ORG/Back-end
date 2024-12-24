from django.db.models.signals import post_save, pre_delete ,pre_save
from django.dispatch import receiver
from .models import Profile
from counseling.models import Psychiatrist
import logging

logger = logging.getLogger(__name__)
@receiver(post_save, sender=Psychiatrist ) 
def create_profile(sender, instance, created, **kwargs):
    if created:
        print( "instance ----------->" , instance)
        print( " sender------------->" , sender )
        Profile.objects.create(psychiatrist=instance)
  

@receiver(post_save, sender=Psychiatrist) 
def save_profile(sender, instance, **kwargs):
        print( "instance ----------->" , instance)
        print( " sender-------------> " , sender )
        logging.warning("here in save profile ")
        if not instance.profile :
            Profile.objects.create(psychiatrist=instance) 
        instance.profile.save()

 
# @receiver(pre_save, sender=Psychiatrist) 
# def checker(sender, instance, **kwargs):
#     if instance.id is None:
#         pass
#     else:
#         save_profile(sender = sender ,  instance = instance , kwargs = kwargs )