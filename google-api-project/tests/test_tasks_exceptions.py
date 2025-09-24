import pytest
from api.models import CalendarEvent
from api.tasks import create_google_calendar_event, update_google_calendar_event, delete_google_calendar_event


@pytest.mark.django_db
def test_create_google_calendar_event_success(mocker, django_user_model):
    mocker.patch("api.tasks.close_old_connections", autospec=True)  # ★追加
    user = django_user_model.objects.create(username="testuser", email="test@example.com")
    event = CalendarEvent.objects.create(
        title="Test Event",
        description="test desc",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
    )

    mock_create = mocker.patch("api.tasks.create_event")
    mock_create.return_value = {"success": True, "google_event_id": "google-event-123"}

    result = create_google_calendar_event(event.id, user.id)

    assert result["success"] is True
    assert result["google_event_id"] == "google-event-123"


@pytest.mark.django_db
def test_create_google_calendar_event_event_not_found(mocker, django_user_model):
    mocker.patch("api.tasks.close_old_connections", autospec=True)  # ★追加
    user = django_user_model.objects.create(username="testuser", email="test@example.com")

    result = create_google_calendar_event(event_id=999, user_id=user.id)

    assert result["success"] is False
    assert "Event 999 not found" in result["message"]


@pytest.mark.django_db
def test_update_google_calendar_event_success(mocker, django_user_model):
    mocker.patch("api.tasks.close_old_connections", autospec=True)  # ★追加
    user = django_user_model.objects.create(username="testuser", email="test@example.com")
    event = CalendarEvent.objects.create(
        title="Test Event",
        description="test desc",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
        google_event_id="google-event-123",
    )

    mock_update = mocker.patch("api.tasks.update_event")
    mock_update.return_value = {"success": True}

    result = update_google_calendar_event(event.id, user.id)

    assert result["success"] is True


@pytest.mark.django_db
def test_delete_google_calendar_event_success(mocker, django_user_model):
    mocker.patch("api.tasks.close_old_connections", autospec=True)  # ★追加
    user = django_user_model.objects.create(username="testuser", email="test@example.com")
    event = CalendarEvent.objects.create(
        title="Test Event",
        description="test desc",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
    )

    mock_delete = mocker.patch("api.tasks.delete_event")
    mock_delete.return_value = {"success": True}

    result = delete_google_calendar_event(event.id, user.id, "google-event-123")

    assert result["success"] is True


@pytest.mark.django_db
def test_delete_google_calendar_event_missing_google_event_id(mocker, django_user_model):
    mocker.patch("api.tasks.close_old_connections", autospec=True)  # ★追加
    user = django_user_model.objects.create(username="testuser", email="test@example.com")
    event = CalendarEvent.objects.create(
        title="Test Event",
        description="",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
    )

    result = delete_google_calendar_event(event.id, user.id, google_event_id=None)

    assert result["success"] is False
    assert f"Event {event.id} has No google_event_id" in result["message"]
