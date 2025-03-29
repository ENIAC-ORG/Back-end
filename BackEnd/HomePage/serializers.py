
from rest_framework import serializers

class DoctorCountSerializer(serializers.Serializer):
    doctor_count = serializers.IntegerField()

class PationtCountSerializer(serializers.Serializer):
    Pationt_count = serializers.IntegerField()

class ReservationCountSerializer(serializers.Serializer):
    reservation_count=serializers.IntegerField()


