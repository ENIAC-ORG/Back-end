from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google_auth_oauthlib.flow import Flow
from .models import OAuthToken
from reservation.models import Reservation
from utils.google_api_helper import is_authorized, create_meet_event, save_tokens
from utils.project_variables import GOOGLE_CLIENT_SECRETS_FILE, SCOPES
import requests
from google.auth.transport.requests import Request
import jwt  
from datetime import datetime, timedelta
from utils.email import send_google_meet_link_to_patient , send_google_meet_link_to_pychiatrist

class GenerateGoogleMeetLinkView(APIView):
    def get(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(pk=reservation_id)
        except Reservation.DoesNotExist:
            return Response({"error": "Reservation not found."}, status=status.HTTP_404_NOT_FOUND)

        psychiatrist = reservation.psychiatrist
        # host_email = psychiatrist.user.email


        if not is_authorized(psychiatrist):
            flow = Flow.from_client_secrets_file(
                GOOGLE_CLIENT_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri='https://eniacgroup.ir/backend/googlemeet/google-oauth-callback/'
            )
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                prompt='consent',
                include_granted_scopes='true'
            )
            request.session['reservation_id'] = reservation_id
            return redirect(authorization_url)


        host_email = OAuthToken.objects.get(psychiatrist=psychiatrist).user_email

        start_time = datetime.strptime(f"{reservation.date} {reservation.time}", "%Y-%m-%d %H:%M:%S")
        end_time = start_time + timedelta(hours=1)

        start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            event = create_meet_event(host_email, start_time, end_time)

            reservation.MeetingLink = event["hangoutLink"]
            reservation.save(update_fields=["MeetingLink"])

            subject = "لینک شرکت در جلسه گوگل میت "
            psychiatrist_name = psychiatrist.get_fullname()
            patient_name = reservation.pationt.get_fullname()
            appointment_date = str(reservation.date)
            appointment_time = str(reservation.time)
            link = event.get('hangoutLink')

            # Send email to patient 
            send_google_meet_link_to_patient(
                subject,
                [reservation.pationt.user.email],
                psychiatrist_name,
                appointment_date,
                appointment_time,
                link
            )
            
            # Send email to pychiatrist 
            send_google_meet_link_to_pychiatrist(
                subject,
                [psychiatrist.user.email],
                patient_name,
                appointment_date,
                appointment_time,
                link
            )

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
            redirect_uri='https://eniacgroup.ir/backend/googlemeet/google-oauth-callback/'
        )

        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials

            # user_email = credentials.id_token.get("email") if credentials.id_token else None
            user_email = None
            if credentials.id_token:
                try:
                    decoded_token = jwt.decode(
                        credentials.id_token,
                        options={"verify_signature": False},  # Disable verification for decoding
                    )
                    user_email = decoded_token.get("email")
                except Exception as e:
                    print(f"Error decoding ID token: {e}")

            if not user_email:
                userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
                response = requests.get(
                    userinfo_endpoint,
                    headers={"Authorization": f"Bearer {credentials.token}"}
                )
                user_email = response.json().get("email")
            
            if not user_email:
                return Response({"error": "Unable to retrieve email from Google OAuth."}, status=400)

            reservation = Reservation.objects.get(pk=reservation_id)
            psychiatrist = reservation.psychiatrist

            save_tokens(user_email, credentials, psychiatrist)

            return redirect(f'https://eniacgroup.ir/backend/googlemeet/generate-meet-link/{reservation_id}/')
        except Exception as e:
            return Response({"error": str(e)}, status=500)
