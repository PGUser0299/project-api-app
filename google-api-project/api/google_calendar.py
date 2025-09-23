from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from .models import GoogleOAuthToken


def get_google_calendar_service(user):
    token = GoogleOAuthToken.objects.get(user=user)
    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return build("calendar", "v3", credentials=creds)


def create_event(user, summary, start_time, end_time, timezone="Asia/Tokyo"):
    service = get_google_calendar_service(user)

    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": timezone},
        "end": {"dateTime": end_time, "timeZone": timezone},
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return created_event


def delete_event(user, event_id):
    service = get_google_calendar_service(user)
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return True