from django.db.models.signals import post_save, pre_delete ,pre_save , post_delete
from django.dispatch import receiver
from .models import MedicalRecordPermission, MedicalRecord
from reservation.models import Reservation


@receiver(post_save, sender=Reservation) 
def create_reservation(sender, instance, created, **kwargs):
    if created:
        print( "instance ----------->" , instance)
        print( " sender------------->" , sender )
        MedicalRecordPermission.objects.create(pationt = instance.pationt , psychiatrist= instance.psychiatrist)


# @receiver(post_save , sender= MedicalRecord)
# def update_medicalrecord(sender, instance, updated, **kwargs):
#     if updated:
#         print( "instance ----------->" , instance)
#         print( " sender------------->" , sender )
        
