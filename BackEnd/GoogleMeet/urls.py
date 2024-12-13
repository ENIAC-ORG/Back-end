from django.urls import path
from .views import GenerateGoogleMeetLinkView, GoogleOAuthCallbackView

urlpatterns = [
    path("generate-meet-link/<int:reservation_id>/", GenerateGoogleMeetLinkView.as_view(), name="generate_meet_link"),
    path("google-oauth-callback/", GoogleOAuthCallbackView.as_view(), name="google_oauth_callback"),
]
