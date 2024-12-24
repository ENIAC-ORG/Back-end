from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google_auth_oauthlib.flow import Flow
from reservation.models import Reservation
from utils.google_api_helper import is_authorized, create_meet_event, save_tokens
from utils.project_variables import GOOGLE_CLIENT_SECRETS_FILE, SCOPES

class GenerateGoogleMeetLinkView(APIView):
    def get(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(pk=reservation_id)
        except Reservation.DoesNotExist:
            return Response({"error": "Reservation not found."}, status=status.HTTP_404_NOT_FOUND)

        host_email = reservation.psychiatrist.user.email

        if not is_authorized(host_email):
            flow = Flow.from_client_secrets_file(
                GOOGLE_CLIENT_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri='https://eniacgroup.ir/googlemeet/google-oauth-callback/'
            )
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            request.session['reservation_id'] = reservation_id
            return redirect(authorization_url)

        start_time = f"{reservation.date}T{reservation.time}:00Z"
        end_time = f"{reservation.date}T{reservation.time}:00Z"  

        try:
            event = create_meet_event(host_email, start_time, end_time)
            reservation.MeetingLink = event["hangoutLink"]
            reservation.save(update_fields=["MeetingLink"])
            
            return redirect(reservation.MeetingLink)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleOAuthCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        reservation_id = request.session.get('reservation_id')

        if not code or not reservation_id:
            return Response({"error": "Invalid authorization flow."}, status=400)

        flow = Flow.from_client_secrets_file(
            GOOGLE_CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri='https://eniacgroup.ir/googlemeet/google-oauth-callback/'
        )

        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            user_email = None
            if credentials.id_token and 'email' in credentials.id_token:
                user_email = credentials.id_token['email']
            
            if not user_email:
                return Response({"error": "Unable to retrieve email from Google OAuth."}, status=400)

            save_tokens(user_email, credentials)

            return redirect(f'/generate-meet-link/{reservation_id}/')
        except Exception as e:
            return Response({"error": str(e)}, status=500)
