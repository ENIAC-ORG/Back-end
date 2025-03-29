from rest_framework import serializers
from counseling.models import  Psychiatrist, Pationt
from .models import Rating
from django.db.models import Q
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('psychiatrist', 'rating', 'comments')

    def run_validation(self, data=...):
        return super().run_validation(data)  
      
    def run_validators(self, value):
        return super().run_validators(value) 
    
    def validate(self, attrs):
        return super().validate(attrs)


# def validate(self, attrs):
#     pationt = attrs['pationt']
#     psychiatrist = attrs['psychiatrist']
#     print(pationt)
#     print(psychiatrist)

#     if Rating.objects.filter(pationt=pationt, psychiatrist=psychiatrist).exists():
#         raise serializers.ValidationError('A patient can only rate a psychiatrist once.')

#     return attrs
