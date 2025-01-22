from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from reservation.models import Psychiatrist
from GoogleMeet.models import OAuthToken 
from google.auth.transport.requests import Request
from utils.project_variables import SCOPES
import json

def is_authorized(host_email):
    """
    Check if a psychiatrist has valid tokens in the database.
    """
    return OAuthToken.objects.filter(user_email=host_email).exists()

def save_tokens(user_email, credentials, psychiatrist):
    """
    Save or update OAuth tokens for a psychiatrist in the database.
    """
    token_data = json.loads(credentials.to_json())
    OAuthToken.objects.update_or_create(
        user_email=user_email, 
        defaults={"token_data": token_data, "psychiatrist": psychiatrist}
    )
    print(f"Tokens saved successfully for {user_email}")

def get_calendar_service(user_email):
    """
    Retrieve the Google Calendar API service for a psychiatrist, refreshing the token if necessary.
    """
    try:
        token = OAuthToken.objects.get(user_email=user_email)
        credentials = Credentials.from_authorized_user_info(token.token_data, SCOPES)
        
        if credentials.expired and credentials.refresh_token:
            # Refresh the access token
            credentials.refresh(Request())
            
            # Update the token data in the database
            token.token_data = json.loads(credentials.to_json())
            token.save()
        
        return build('calendar', 'v3', credentials=credentials)
    except OAuthToken.DoesNotExist:
        raise Exception(f"No valid credentials found for {user_email}")
    except Exception as e:
        raise Exception(f"Error while accessing credentials: {e}")

def create_meet_event(host_email, start_time, end_time, summary="Google Meet Event"):
    """
    Create a Google Meet event and return the event details.
    """
    service = get_calendar_service(host_email)

    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
        "attendees": [{"email": host_email}],
        "conferenceData": {
            "createRequest": {
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
                "requestId": "random-string-id",
            }
        },
    }

    event = service.events().insert(
        calendarId="primary", body=event, conferenceDataVersion=1
    ).execute()

    return event
