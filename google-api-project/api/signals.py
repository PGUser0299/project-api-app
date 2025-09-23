from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import CalendarEvent
from .tasks import delete_google_calendar_event


@receiver(post_delete, sender=CalendarEvent)
def on_event_deleted(sender, instance, **kwargs):
    """CalendarEvent が削除されたら Google Calendar からも削除"""
    user_id = instance.created_by.id if instance.created_by else None
    if instance.google_event_id and user_id:
        delete_google_calendar_event.delay(instance.id, user_id)