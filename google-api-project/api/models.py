from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class GoogleOAuthToken(models.Model):
    """Google OAuth2 トークンをユーザー単位で管理"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="google_token")
    access_token = models.TextField(help_text="最新のアクセストークン")
    refresh_token = models.TextField(blank=True, null=True, help_text="リフレッシュトークン（初回ログイン時のみ返却される）")
    client_id = models.CharField(max_length=255, help_text="Google API Client ID")
    client_secret = models.CharField(max_length=255, help_text="Google API Client Secret")
    token_uri = models.CharField(
        max_length=255,
        default="https://oauth2.googleapis.com/token",
        help_text="Google OAuth2 トークンエンドポイント"
    )
    expires_in = models.IntegerField(help_text="アクセストークンの有効期限（秒）", default=3600)

    created_at = models.DateTimeField(auto_now_add=True, help_text="初回保存日時")
    updated_at = models.DateTimeField(auto_now=True, help_text="最終更新日時")

    def __str__(self):
        return f"GoogleOAuthToken(user={self.user.username}, updated_at={self.updated_at})"


class CalendarEvent(models.Model):
    """アプリ内イベント（Google Calendar と同期対象）"""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
        null=True,
        blank=True,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="events_participating",
        blank=True,
    )
    google_event_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"
