from rest_framework import serializers
from counseling.models import Psychiatrist
from reservation.models import Reservation
from .models import FreeTime

    
class ReservationListSerializer(serializers.ModelSerializer):
    patient_full_name = serializers.SerializerMethodField()
    class Meta:
        model = Reservation
        fields = ["date", "day", "time", "type", "MeetingLink","pationt","patient_full_name"]

    def get_patient_full_name(self, obj):
        pationt = obj.pationt
        user = pationt.user
        return f"{user.firstname} {user.lastname}"
    
    def validate(self, attrs):
        return super().validate(attrs)
    

class FreeTimeSerializer(serializers.ModelSerializer):
    time = serializers.CharField()
    class Meta :
        model = FreeTime
        fields = ['month','day', 'time']

    def validate(self, attrs):
        if not attrs.get('month') or not attrs.get('day') or not attrs.get('time'):
            raise serializers.ValidationError('All fields are required.')
        return attrs
    

class GETFreeTimeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FreeTime
        fields = ['month', 'day', 'time', 'date']  

    def validate(self, attrs):
        return super().validate(attrs)
    
class FreeTimeByDateSerializer(serializers.ModelSerializer):
    oldtime = serializers.CharField()
    newtime = serializers.CharField()
    class Meta:
        model = FreeTime
        fields = ['date', 'oldtime', 'newtime']  

    def validate(self, attrs):
        return super().validate(attrs)
    
class DoctorInfoSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = Psychiatrist
        fields = ['image', 'field', 'clinic_address', 'clinic_telephone_number','doctorate_code',  'fullname','description']
        read_only_fields = ('doctorate_code',)

    def get_fullname(self, obj):
        return obj.get_fullname()
    
    def validate(self, attrs):
        if not attrs.get('field'):
            raise serializers.ValidationError('Field is required.')
        return attrs