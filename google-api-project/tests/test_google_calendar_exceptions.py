import pytest
from api.google_calendar import (
    get_credentials,
    update_event,
    delete_event,
)
from api.models import GoogleOAuthToken, CalendarEvent
from google.auth.exceptions import RefreshError


@pytest.mark.django_db
def test_get_credentials_token_not_found(django_user_model):
    user = django_user_model.objects.create(username="nouser", email="nouser@example.com")
    creds, error = get_credentials(user, ["scope"])
    assert creds is None
    assert error["success"] is False
    assert "No Google token found" in error["message"]


@pytest.mark.django_db
def test_get_credentials_refresh_error(mocker, django_user_model):
    user = django_user_model.objects.create(username="refreshfail", email="refreshfail@example.com")
    GoogleOAuthToken.objects.create(
        user=user,
        access_token="dummy",
        refresh_token="dummy",
        token_uri="http://dummy",
        client_id="id",
        client_secret="secret",
    )
    mocker.patch("google.oauth2.credentials.Credentials.refresh", side_effect=RefreshError())
    mocker.patch(
        "google.oauth2.credentials.Credentials.expired",
        new_callable=mocker.PropertyMock,
        return_value=True,
    )

    creds, error = get_credentials(user, ["scope"])
    assert creds is None
    assert "Failed to refresh" in error["message"]


@pytest.mark.django_db
def test_update_event_missing_google_event_id(django_user_model):
    user = django_user_model.objects.create(username="nogid", email="nogid@example.com")
    GoogleOAuthToken.objects.create(
        user=user,
        access_token="dummy",
        refresh_token="dummy",
        token_uri="http://dummy",
        client_id="id",
        client_secret="secret",
    )
    event = CalendarEvent.objects.create(
        title="No GID Event",
        description="",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
        google_event_id=None,
    )
    result = update_event(user, event)
    assert result["success"] is False
    assert "No google_event_id" in result["message"]


@pytest.mark.django_db
def test_delete_event_missing_google_event_id_with_token(django_user_model):
    """トークン有り + google_event_id 無し"""
    user = django_user_model.objects.create(username="nogid2", email="nogid2@example.com")
    GoogleOAuthToken.objects.create(
        user=user,
        access_token="dummy",
        refresh_token="dummy",
        token_uri="http://dummy",
        client_id="id",
        client_secret="secret",
    )
    event = CalendarEvent.objects.create(
        title="No GID Event 2",
        description="",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
        google_event_id=None,
    )
    result = delete_event(user, event)
    assert result["success"] is False
    assert "No google_event_id" in result["message"]


@pytest.mark.django_db
def test_delete_event_no_token(django_user_model):
    """トークン無し"""
    user = django_user_model.objects.create(username="notoken", email="notoken@example.com")
    event = CalendarEvent.objects.create(
        title="Event no token",
        description="",
        start_time="2025-09-19T10:00:00Z",
        end_time="2025-09-19T11:00:00Z",
        google_event_id="dummyid",
    )
    result = delete_event(user, event)
    assert result["success"] is False
    assert "No Google token found" in result["message"]
