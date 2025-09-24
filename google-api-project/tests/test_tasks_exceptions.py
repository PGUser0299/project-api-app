import pytest
from api.models import CalendarEvent, User
from api.tasks import create_google_calendar_event, update_google_calendar_event, delete_google_calendar_event


@pytest.mark.django_db
def test_create_google_calendar_event(mocker):
    user = User.objects.create(username="testuser", email="test@example.com")
    event = CalendarEvent.objects.create(
        title="Test Event",
        description="test desc",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
    )

    mock_create = mocker.patch("api.tasks.create_event")
    mock_create.return_value = {"success": True, "data": {"id": "google-event-123"}}

    result = create_google_calendar_event(event.id, user.id)

    assert result["success"]
    assert result["data"]["id"] == "google-event-123"
    mock_create.assert_called_once()


@pytest.mark.django_db
def test_update_google_calendar_event(mocker):
    user = User.objects.create(username="testuser", email="test@example.com")
    event = CalendarEvent.objects.create(
        title="Test Event",
        description="test desc",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
        google_event_id="google-event-123",
    )

    mock_update = mocker.patch("api.tasks.update_event")
    mock_update.return_value = {"success": True, "data": {"id": "google-event-123"}}

    result = update_google_calendar_event(event.id, user.id)

    assert result["success"]
    mock_update.assert_called_once()


@pytest.mark.django_db
def test_delete_google_calendar_event(mocker):
    user = User.objects.create(username="testuser", email="test@example.com")
    event = CalendarEvent.objects.create(
        title="Test Event",
        description="test desc",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
        google_event_id="google-event-123",
    )

    mock_delete = mocker.patch("api.tasks.delete_event")
    mock_delete.return_value = {"success": True}

    result = delete_google_calendar_event(event.id, user.id)

    assert result["success"]
    mock_delete.assert_called_once()
