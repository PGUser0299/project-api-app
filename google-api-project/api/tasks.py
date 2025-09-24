from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from .models import CalendarEvent
from .google_calendar import create_event, update_event, delete_event

User = get_user_model()


def _get_event_and_user(event_id, user_id):
    """共通: イベントとユーザーを取得"""
    try:
        event = CalendarEvent.objects.get(id=event_id)
        user = User.objects.get(id=user_id)
        return event, user, None
    except CalendarEvent.DoesNotExist:
        return None, None, {"success": False, "message": f"Event {event_id} not found"}
    except User.DoesNotExist:
        return None, None, {"success": False, "message": f"User {user_id} not found"}
    except Exception as e:
        return None, None, {"success": False, "message": f"Unexpected error: {e}"}


@shared_task
def create_google_calendar_event(event_id, user_id):
    close_old_connections()
    event, user, error = _get_event_and_user(event_id, user_id)
    if error:
        return error
    result = create_event(user, event)
    close_old_connections()
    return result


@shared_task
def update_google_calendar_event(event_id, user_id):
    close_old_connections()
    event, user, error = _get_event_and_user(event_id, user_id)
    if error:
        return error
    result = update_event(user, event)
    close_old_connections()
    return result


@shared_task
def delete_google_calendar_event(event_id, user_id, google_event_id):
    event, user, error = _get_event_and_user(event_id, user_id)
    if error:
        return error
    if not google_event_id:
        return {"success": False, "message": f"Event {event_id} has No google_event_id"}

    return delete_event(user, event)