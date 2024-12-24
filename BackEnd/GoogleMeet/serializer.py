# from rest_framework import serializers

# class GoogleMeetSerializer(serializers.Serializer):
#     reservation_id = serializers.IntegerField()
#     def create(self, validated_data):

#         reservation_id = validated_data['Reservation_id']
#         return {
#             'reservation_id' :reservation_id,
#         }

#     def update(self, instance, validated_data):
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         return instance
