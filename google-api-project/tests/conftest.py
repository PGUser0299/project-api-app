import pytest
from unittest.mock import patch
from api.models import GoogleOAuthToken


@pytest.fixture(autouse=True)
def use_sqlite(settings):
    """全テストでDBをSQLite（メモリDB）に切り替える。"""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


@pytest.fixture
def mock_google_token():
    """固定のダミーユーザーを返す。"""
    with patch.object(GoogleOAuthToken.objects, "get") as mock_get:
        mock_get.return_value = GoogleOAuthToken(
            id=1,
            user_id=999,  # ダミーユーザーID
            access_token="fake-access-token",
            refresh_token="fake-refresh-token",
        )
        yield mock_get
