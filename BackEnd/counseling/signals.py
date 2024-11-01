from django.db.models.signals import post_save, pre_delete ,pre_save , post_delete
from django.dispatch import receiver
from counseling.models import Psychiatrist , Pationt 
 

@receiver(post_delete , sender= Pationt ) 
@receiver(post_delete , sender= Psychiatrist ) 
def delete_associated_user( sender , instance , **kwargs ) : 
    instance.user.delete()