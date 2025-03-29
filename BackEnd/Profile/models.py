from django.db import models
from counseling.models import Psychiatrist
from django.core.exceptions import ValidationError

class Profile(models.Model):
    psychiatrist = models.OneToOneField(Psychiatrist, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='images\doctors\profile_pics')
    profile_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not isinstance(self.psychiatrist , Psychiatrist):
            raise ValidationError('Invalid value for content_object')
        self.name = self.determine_name(self.name)
        self.profile_type = self.determine_profile_type()
        self.image = self.determine_image()
        super().save(*args, **kwargs)


    def determine_image(self):
        if not self.pk:
            var = self.psychiatrist.get_profile_image()
            print(var)
            return var
        return self.image


    def determine_name(self, name):
        if not self.pk:
            return self.psychiatrist.get_fullname()
        return name

    def determine_profile_type(self): 
        if not self.pk : 
            return self.psychiatrist.field 
        return self.profile_type

