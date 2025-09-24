import pytest
from unittest.mock import patch
from api.models import GoogleOAuthToken


@pytest.fixture(scope="session")
def django_db_setup():
    """pytest-django が使うDB設定を SQLite に差し替え"""
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }


@pytest.fixture
def mock_google_token():
    """固定のダミートークンを返す"""
    with patch.object(GoogleOAuthToken.objects, "get") as mock_get:
        mock_get.return_value = GoogleOAuthToken(
            id=1,
            user_id=999,
            access_token="fake-access-token",
            refresh_token="fake-refresh-token",
            token_uri="dummy",
            client_id="dummy",
            client_secret="dummy",
        )
        yield mock_get
