from django.urls import path
from .views import *

urlpatterns = [
   path("",GoogleMeetLinkAPIView.as_view(),name="CreateGoogleMeet"),
   # path("Get/",GetSpaceView.as_view(), name="GetGoogleMeet"),
   # path("End/",EndSpaceView.as_view(),name="EndGoogleMeet"),
   # path("Authenticate/",GoogleMeetAuthView.as_view(),name="GoogleMeetAuthView"),
   
]
