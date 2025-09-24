from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request as GoogleRequest
from django.contrib.auth import get_user_model
from .models import GoogleOAuthToken, CalendarEvent

User = get_user_model()


def get_credentials(user, scopes):
    token = GoogleOAuthToken.objects.filter(user=user).first()
    if not token:
        return None, {"success": False, "message": "No Google token for user"}

    creds = Credentials(
        token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=scopes,
    )

    if creds and not creds.valid and creds.refresh_token:
        try:
            creds.refresh(GoogleRequest())
            token.access_token = creds.token
            token.save(update_fields=["access_token"])
        except RefreshError as e:
            return None, {"success": False, "message": f"Failed to refresh: {e}"}

    return creds, None


def build_calendar_service(user):
    """Google Calendar API サービスを構築"""
    creds, error = get_credentials(user, ["https://www.googleapis.com/auth/calendar"])
    if error:
        return None, error

    try:
        service = build("calendar", "v3", credentials=creds)
        return service, None
    except Exception as e:
        return None, {"success": False, "message": f"Failed to build service: {e}"}


def safe_execute(request):
    """Google API リクエストを安全に実行"""
    try:
        response = request.execute()
        return {"success": True, "data": response}
    except HttpError as e:
        return {"success": False, "message": f"Google API error: {e}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {e}"}


def _build_event_body(event: CalendarEvent):
    """Google Calendar API 用イベント body を作成"""
    return {
        "summary": event.title,
        "description": event.description,
        "start": {"dateTime": event.start_time.isoformat(), "timeZone": "Asia/Tokyo"},
        "end": {"dateTime": event.end_time.isoformat(), "timeZone": "Asia/Tokyo"},
    }


def create_event(user, event: CalendarEvent):
    """Google カレンダーにイベント作成"""
    service, error = build_calendar_service(user)
    if error:
        return error

    result = safe_execute(
        service.events().insert(calendarId="primary", body=_build_event_body(event))
    )

    if result["success"]:
        event.google_event_id = result["data"]["id"]
        event.save(update_fields=["google_event_id"])
    return result


def update_event(user, event: CalendarEvent):
    """Google カレンダーイベント更新"""
    service, error = build_calendar_service(user)
    if error:
        return error
    if not event.google_event_id:
        return {"success": False, "message": f"Event {event.id} has No google_event_id"}

    return safe_execute(
        service.events().update(
            calendarId="primary",
            eventId=event.google_event_id,
            body=_build_event_body(event),
        )
    )


def delete_event(user, event: CalendarEvent):
    """Google カレンダーイベント削除"""
    service, error = build_calendar_service(user)
    if error:
        return error
    if not event.google_event_id:
        return {"success": False, "message": f"Event {event.id} has No google_event_id"}

    return safe_execute(
        service.events().delete(calendarId="primary", eventId=event.google_event_id)
    )
