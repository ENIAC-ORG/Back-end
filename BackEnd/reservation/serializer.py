from rest_framework import serializers
from Doctorpanel.models import FreeTime
from accounts.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import password_validation
from django.core import exceptions as exception
from .models import Reservation 
from datetime import date


class ReserveSerializer(serializers.ModelSerializer ) : 
    class Meta : 
        model = Reservation 
        fields = ["day" , "type" , "date" , "time" , "id" , "psychiatrist"]

    def validate(self, attrs):
        return super().validate(attrs)    

class CreateReserveSerializer(serializers.ModelSerializer): 
    doctor_id = serializers.IntegerField()
    class Meta : 
        model = Reservation 
        fields = [ "type" , "date" , "time" , "doctor_id" , "id"]

    def validate(self, attrs):
        return super().validate(attrs)    
    
    # def validate_date(self ,attrs )

class DaySerializer(serializers.Serializer) : 
    date = serializers.DateField()    
    doctor_id = serializers.IntegerField()
    class Meta : 
        model = Reservation 
        fields = ["date" , "doctor_id"]
    def validate(self, attrs):
        return super().validate(attrs)    
   
class BetweenDatesSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    doctor_id = serializers.IntegerField()

    class Meta : 
        model = Reservation 
        fields = ["start_date" , "end_date" , "doctor_id"]
        
    def validate(self, attrs):
        return super().validate(attrs)    
    

class GETFreeTimeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FreeTime
        fields = ['month', 'day', 'time', 'date']  

    def validate(self, attrs):
        return super().validate(attrs)