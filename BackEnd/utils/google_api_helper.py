from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils.project_variables import SCOPES
import json
import os
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "multi_user_token.json")



def is_authorized(user_email):
    if os.path.exists(TOKEN_FILE) and os.stat(TOKEN_FILE).st_size > 0:
        with open(TOKEN_FILE, 'r') as token:
            try:
                tokens = json.load(token)
                return user_email in tokens
            except json.JSONDecodeError:
                print("Token file is blank or corrupted.")
                return False
    return False


def save_tokens(user_email, credentials):
    user_token = json.loads(credentials.to_json())
    tokens = {}

    if os.path.exists(TOKEN_FILE) and os.stat(TOKEN_FILE).st_size > 0:
        with open(TOKEN_FILE, 'r') as token:
            try:
                tokens = json.load(token)
            except json.JSONDecodeError:
                print("Token file is blank or corrupted. Resetting.")
                tokens = {}

    tokens[user_email] = user_token

    with open(TOKEN_FILE, 'w') as token:
        json.dump(tokens, token, indent=4)

    print(f"Tokens saved successfully for {user_email}")


def get_calendar_service(user_email):
    if os.path.exists(TOKEN_FILE) and os.stat(TOKEN_FILE).st_size > 0:
        with open(TOKEN_FILE, 'r') as token:
            tokens = json.load(token)
            user_token = tokens.get(user_email)
            if user_token:
                credentials = Credentials.from_authorized_user_info(user_token, SCOPES)
                return build('calendar', 'v3', credentials=credentials)
    raise Exception(f"No valid credentials found for {user_email}")


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
                "requestId": "random-string-id",
            }
        },
    }

    event = service.events().insert(
        calendarId="primary", body=event, conferenceDataVersion=1
    ).execute()

    return event