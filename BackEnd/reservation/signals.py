from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reservation
from rest_framework.test import APIRequestFactory  

# @receiver(post_save, sender=Reservation)
# def create_google_meet_link(sender, instance, created, **kwargs):
#     if created and instance.type == 'مجازی':
#         factory = APIRequestFactory()
#         request = factory.post('/api/googlemeet/', {
#             'reservation_id': instance.id
#         }, format='json')
        
#         google_meet_api_view = GoogleMeetAPIView.as_view()
#         response = google_meet_api_view(request)
        
#         if response.status_code == 201:
#             print('Google Meet link created successfully.')
#         else:
#             print('Failed to create Google Meet link.')
