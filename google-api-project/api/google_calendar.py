from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from .models import GoogleOAuthToken, CalendarEvent


def get_credentials(user, scopes):
    """ユーザーのGoogle OAuthトークンからCredentialsを生成"""
    try:
        token = GoogleOAuthToken.objects.get(user=user)
    except GoogleOAuthToken.DoesNotExist:
        return None, {"success": False, "message": "No Google token found"}

    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=scopes,
    )

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            return None, {"success": False, "message": "Failed to refresh token"}

    return creds, None


def _get_service(user):
    """Google API service を取得"""
    creds, error = get_credentials(user, ["https://www.googleapis.com/auth/calendar"])
    if error:
        raise Exception(error["message"])
    return build("calendar", "v3", credentials=creds)


def create_event(user, event: CalendarEvent):
    try:
        service = _get_service(user)
        body = {
            "summary": event.title,
            "description": event.description,
            "start": {"dateTime": event.start_time.isoformat()},
            "end": {"dateTime": event.end_time.isoformat()},
        }
        created_event = service.events().insert(calendarId="primary", body=body).execute()
        event.google_event_id = created_event["id"]
        event.save(update_fields=["google_event_id"])
        return {"success": True, "google_event_id": created_event["id"]}
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_event(user, event: CalendarEvent):
    if not event.google_event_id:
        return {"success": False, "message": "No google_event_id to update"}

    try:
        service = _get_service(user)
        body = {
            "summary": event.title,
            "description": event.description,
            "start": {"dateTime": event.start_time.isoformat()},
            "end": {"dateTime": event.end_time.isoformat()},
        }
        service.events().update(
            calendarId="primary", eventId=event.google_event_id, body=body
        ).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}


def delete_event(user, event: CalendarEvent):
    if not event.google_event_id:
        return {"success": False, "message": "No google_event_id to delete"}

    try:
        service = _get_service(user)
        service.events().delete(
            calendarId="primary", eventId=event.google_event_id
        ).execute()
        event.google_event_id = None
        event.save(update_fields=["google_event_id"])
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}
