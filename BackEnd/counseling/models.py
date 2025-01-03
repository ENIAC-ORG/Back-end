from typing import Any
from django.db import models
# from accounts.models import User
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError 
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model

class Psychiatrist(models.Model ) : 
    TYPE_INDIVIDUAL = "فردی"
    TYPE_KIDS =  "کودک"
    TYPE_COUPLES = "زوج"
    TYPE_TEEN  = "نوجوان"
    TYPE_FAMILY = "خانواده"
    TYPE_EDUCATIONAL = "تحصیلی"
    TYPE_COUCHING = "کوچینگ"
    TYPE_CLINICAL = "بالینی"
    TYPE_PSYCLOGICAL = "روان پزشکی"
    TYPE_USER = "defualt"
    CHOICES = (
        (TYPE_INDIVIDUAL , "فردی") , 
        (TYPE_COUPLES , "زوج") , 
        (TYPE_KIDS , "کودک") , 
        (TYPE_TEEN , "نوجوان") ,
        (TYPE_EDUCATIONAL , 'تحصیلی') , 
        (TYPE_FAMILY , 'خانواده') , 
        (TYPE_COUCHING , 'کوچینگ') ,
        (TYPE_CLINICAL , "بالینی") ,
        (TYPE_PSYCLOGICAL,"روان پزشکی")
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE , unique=True )
    image = models.ImageField(upload_to='images/doctors/profile_pics', null=True,blank=True )  #, default='images/doctors/profile_pics/default.png')
    field = models.CharField( max_length=255, choices=CHOICES , default=TYPE_USER,null=True, blank= True)
    clinic_address = models.TextField(null=True, blank=True)  # Clinic address, allowing multiline text
    clinic_telephone_number = models.CharField(max_length=15, null=True, blank=True)
    doctorate_code = models.CharField(max_length=50, blank=True,unique=True, null=True)
    description = models.TextField(blank=True, null=True)

    def get_default_profile_image(self):
    
        if self.user.gender == 'M':
            res =  'images/doctors/profile_pics/male_default.png'   ## settings.MEDIA_URL + 
            return res
        else:
            res = 'images/doctors/profile_pics/female_default.png'
            return res

    def get_profile_image(self ) :
        if  not self.image : 
            var = self.get_default_profile_image()
            return var 
        else : 
            VAR =   str(self.image  )  #settings.MEDIA_URL +
            print(VAR)
            return VAR
        
    def get_fullname(self) :
        return str(self.user.firstname) + " " + str(self.user.lastname)

    def save(self, *args, **kwargs):
        User = get_user_model()
        """
        Check if there's already a Psychiatrist object associated with this User
        """ 
        if Pationt.objects.filter(user=self.user).exists() :
            raise ValidationError("a patient could not be register as a doctor")
        if not self.user.role == 'doctor':
            self.user.role = User.TYPE_DOCTOR
            self.user.save()
        super().save(*args, **kwargs)

class Pationt( models.Model ) : 
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE , unique=True )
   # telegramAccount = models.OneToOneField(TelegramAccount , on_delete=models.CASCADE,null=True , blank=True ) 
    def get_fullname(self) :
        return str(self.user.firstname) + " " + str(self.user.lastname)
    def save(self, *args, **kwargs):
        """
        Check if there's already a Pationt object associated with this User
        """ 
        if Psychiatrist.objects.filter(user=self.user).exists() :
            raise ValidationError("a doctor could not be register as a patient")
        return super().save(*args, **kwargs)
    