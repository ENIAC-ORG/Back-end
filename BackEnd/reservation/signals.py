# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Reservation
# from rest_framework.test import APIRequestFactory
# from GoogleMeet.views import GoogleMeetLinkAPIView

# @receiver(post_save, sender=Reservation)
# def create_google_meet_link(sender, instance, created, **kwargs):
#     if created and instance.type == 'مجازی':
#         host_email = instance.psychiatrist.user.email  
#         patient_email = instance.pationt.user.email  
#         psychiatrist_name = instance.psychiatrist.user.firstname + ' ' + instance.psychiatrist.user.lastname
#         start_date = instance.date
#         start_time = instance.time
#         start_datetime = f"{start_date}T{start_time}:00Z" 
#         end_datetime = f"{start_date}T{(start_time.hour + 1)}:{start_time.minute}:00Z"  

#         factory = APIRequestFactory()
#         request = factory.post(
#             'https://eniacgroup.ir/googlemeet',
#             {
#                 "host_email": host_email,
#                 "start_time": start_datetime,
#                 "end_time": end_datetime,
#                 "patient_email": patient_email,
#                 "psychiatrist_name": psychiatrist_name
#             },
#             format='json'
#         )

#         google_meet_api_view = GoogleMeetLinkAPIView.as_view()
#         response = google_meet_api_view(request)

#         if response.status_code == 201:
#             instance.MeetingLink = response.data.get("meet_link")
#             instance.save(update_fields=["MeetingLink"])
#         else:
#             print(f"Failed to create Google Meet link: {response.data.get('error')}")
