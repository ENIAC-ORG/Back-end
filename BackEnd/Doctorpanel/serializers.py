from rest_framework import serializers
from counseling.models import Psychiatrist
from reservation.models import Reservation
from .models import FreeTime

class DoctorPanelSerializer(serializers.Serializer):
    psychiatrist_id = serializers.IntegerField()
    class Meta :
        model = Psychiatrist
        fields = ["psychiatrist_id"]
    def validate(self, attrs):
        return super().validate(attrs) 
    

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
        return super().validate(attrs)