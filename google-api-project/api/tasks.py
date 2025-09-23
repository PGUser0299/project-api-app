import base64
from decouple import config
from dotenv import load_dotenv, find_dotenv
from celery import shared_task
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from django.conf import settings
from django.contrib.auth import get_user_model
from email.mime.text import MIMEText
from .models import CalendarEvent, GoogleOAuthToken

load_dotenv(find_dotenv())


@shared_task
def send_gmail_notification(to_email, subject, body, user_id):
    """ユーザーの Gmail を使ってメール送信"""
    try:
        token = GoogleOAuthToken.objects.get(user_id=user_id)
    except GoogleOAuthToken.DoesNotExist:
        return f"No Google token for user {user_id}"

    creds = Credentials(
        token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )

    if not creds.valid and creds.refresh_token:
        creds.refresh(GoogleRequest())

    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(userId="me", body={"raw": raw}).execute()

    return f"Email sent to {to_email}"


@shared_task
def create_google_calendar_event(event_id, user_id):
    """ユーザーのカレンダーにイベントを作成"""
    try:
        event = CalendarEvent.objects.get(id=event_id)
    except CalendarEvent.DoesNotExist:
        return f"Event {event_id} not found"

    try:
        token = GoogleOAuthToken.objects.get(user_id=user_id)
    except GoogleOAuthToken.DoesNotExist:
        return f"No Google token for user {user_id}"

    creds = Credentials(
        token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )

    if not creds.valid and creds.refresh_token:
        creds.refresh(GoogleRequest())

    service = build("calendar", "v3", credentials=creds)

    attendees = [{"email": p.email} for p in event.participants.all()]

    event_body = {
        "summary": event.title,
        "description": event.description,
        "start": {"dateTime": event.start_time.isoformat(), "timeZone": "Asia/Tokyo"},
        "end": {"dateTime": event.end_time.isoformat(), "timeZone": "Asia/Tokyo"},
        "attendees": attendees,
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event_body,
        sendUpdates="all",
    ).execute()

    event.google_event_id = created_event.get("id")
    event.save(update_fields=["google_event_id"])

    return f"Event {event.id} created in Google Calendar"


@shared_task
def delete_google_calendar_event(event_id, user_id, google_event_id=None):
    """Google Calendar からイベントを削除"""
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"User {user_id} not found"

    try:
        token_obj = GoogleOAuthToken.objects.get(user=user)
    except GoogleOAuthToken.DoesNotExist:
        return f"No Google token for user {user.email}"

    creds = Credentials(
        token=token_obj.access_token,
        refresh_token=token_obj.refresh_token,
        token_uri=token_obj.token_uri,   
        client_id=token_obj.client_id,
        client_secret=token_obj.client_secret,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )

    if not creds.valid and creds.refresh_token:
        creds.refresh(GoogleRequest())

    service = build("calendar", "v3", credentials=creds)
    calendar_id = "primary"

    # DBから既に削除済みなら google_event_id を使う
    if not google_event_id:
        try:
            event = CalendarEvent.objects.get(id=event_id, created_by=user)
            google_event_id = event.google_event_id
        except CalendarEvent.DoesNotExist:
            return f"Event {event_id} not found in DB"

    if not google_event_id:
        return f"Event {event_id} has no google_event_id"

    try:
        service.events().delete(calendarId=calendar_id, eventId=google_event_id).execute()
        return f"Event {event_id} deleted from Google Calendar"
    except Exception as e:
        return f"Failed to delete event {event_id} from Google Calendar: {e}"


@shared_task
def update_google_calendar_event(event_id, user_id):
    """ユーザーのカレンダーにあるイベントを更新 (参加者含む)"""
    try:
        event = CalendarEvent.objects.get(id=event_id)
    except CalendarEvent.DoesNotExist:
        return f"Event {event_id} not found"

    try:
        token = GoogleOAuthToken.objects.get(user_id=user_id)
    except GoogleOAuthToken.DoesNotExist:
        return f"No Google token for user {user_id}"

    creds = Credentials(
        token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )

    if not creds.valid and creds.refresh_token:
        creds.refresh(GoogleRequest())

    service = build("calendar", "v3", credentials=creds)

    if not event.google_event_id:
        return f"Event {event.id} has no google_event_id"

    attendees = [{"email": p.email} for p in event.participants.all()]

    event_body = {
        "summary": event.title,
        "description": event.description,
        "start": {"dateTime": event.start_time.isoformat(), "timeZone": "Asia/Tokyo"},
        "end": {"dateTime": event.end_time.isoformat(), "timeZone": "Asia/Tokyo"},
        "attendees": attendees,
    }

    service.events().update(
        calendarId="primary",
        eventId=event.google_event_id,
        body=event_body,
        sendUpdates="all",
    ).execute()

    return f"Event {event.id} updated in Google Calendar (participants synced)"
