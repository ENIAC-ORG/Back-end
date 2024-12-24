from django.db import models
from counseling.models import Psychiatrist
# Create your models here.
class DoctorPersonalityInfo(models.Model ) : 
    psychiatrist = models.OneToOneField( Psychiatrist,on_delete= models.CASCADE )
    text_info = models.TextField( max_length= 600 )
