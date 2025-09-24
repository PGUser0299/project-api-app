import pytest
from django.contrib.auth.models import User
from api.models import CalendarEvent

@pytest.mark.django_db
def test_event_deleted_triggers_task(mocker):
    """google_event_id と created_by がある場合にタスクが呼ばれる"""
    user = User.objects.create(username="deleter", email="deleter@example.com")
    event = CalendarEvent.objects.create(
        title="To be deleted",
        description="test",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
        google_event_id="gid-123",
        created_by=user,
    )
    event_id = event.id  # 削除前に保持しておく

    mock_task = mocker.patch("api.signals.delete_google_calendar_event.delay")

    event.delete()

    mock_task.assert_called_once_with(event_id, user.id)
