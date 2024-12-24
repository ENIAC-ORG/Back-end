from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils.project_variables import SCOPES
import json
import os

TOKEN_FILE = "multi_user_token.json"

def is_authorized(user_email):
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token:
            tokens = json.load(token)
            return user_email in tokens
    return False

def save_tokens(user_email, credentials):
    user_token = json.loads(credentials.to_json())

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token:
            tokens = json.load(token)
    else:
        tokens = {}

    tokens[user_email] = user_token

    with open(TOKEN_FILE, 'w') as token:
        json.dump(tokens, token)

def get_calendar_service(user_email):
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token:
            tokens = json.load(token)
            user_token = tokens.get(user_email)
            if user_token:
                credentials = Credentials.from_authorized_user_info(user_token, SCOPES)
                return build('calendar', 'v3', credentials=credentials)
    raise Exception(f"No valid credentials for {user_email}")

def create_meet_event(host_email, start_time, end_time, summary="Google Meet Event"):
    service = get_calendar_service(host_email)

    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
        "attendees": [{"email": host_email}],
        "conferenceData": {
            "createRequest": {
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
                "requestId": "unique-request-id",
            }
        },
    }

    event = service.events().insert(
        calendarId="primary", body=event, conferenceDataVersion=1
    ).execute()

    return event
