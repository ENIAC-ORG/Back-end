# google_api_helper.py

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import json

from .project_variables import GOOGLE_CLIENT_SECRETS_FILE, SCOPES

def get_calendar_service(user_email):
    # Use a single token file for multiple users
    token_file = "multi_user_token.json"
    credentials = None

    # Load the token file if it exists
    if os.path.exists(token_file):
        with open(token_file, 'r') as token:
            tokens = json.load(token)
            user_token = tokens.get(user_email)
            if user_token:
                credentials = Credentials.from_authorized_user_info(user_token, SCOPES)

    # If no valid credentials, authenticate the user
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_authorized_server(port=8080)

            # Save the credentials back to the token file
            user_token = json.loads(credentials.to_json())
            if os.path.exists(token_file):
                with open(token_file, 'r') as token:
                    tokens = json.load(token)
            else:
                tokens = {}
            tokens[user_email] = user_token
            with open(token_file, 'w') as token:
                json.dump(tokens, token)

    return build('calendar', 'v3', credentials=credentials)

def create_meet_event(host_email, start_time, end_time, summary="Google Meet Event"):
    service = get_calendar_service(host_email)  # Use the psychiatrist's credentials

    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
        "attendees": [{"email": host_email}],
        "organizer": {"email": host_email},  # Ensure host_email is the organizer
        "conferenceData": {
            "createRequest": {
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
                "requestId": "random-string-id"
            }
        }
    }

    event = (
        service.events()
        .insert(calendarId='primary', body=event, conferenceDataVersion=1)
        .execute()
    )
    return event



# signals.py

