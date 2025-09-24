from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class GoogleOAuthToken(models.Model):
    """Google OAuth2 トークンをユーザー単位で管理"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="google_token",
        help_text="このユーザーに紐づくGoogle OAuth2トークン",
    )
    access_token = models.TextField(help_text="最新のアクセストークン")
    refresh_token = models.TextField(
        blank=True,
        null=True,
        help_text="リフレッシュトークン（初回ログイン時のみ返却される）",
    )
    client_id = models.CharField(max_length=255, help_text="Google API Client ID")
    client_secret = models.CharField(max_length=255, help_text="Google API Client Secret")
    token_uri = models.CharField(
        max_length=255,
        default="https://oauth2.googleapis.com/token",
        help_text="Google OAuth2 トークンエンドポイント",
    )
    expires_in = models.IntegerField(
        help_text="アクセストークンの有効期限（秒）",
        default=3600,
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="初回保存日時")
    updated_at = models.DateTimeField(auto_now=True, help_text="最終更新日時")

    def __str__(self):
        return f"GoogleOAuthToken(user={self.user}, updated_at={self.updated_at})"


class CalendarEvent(models.Model):
    """アプリ内イベント（Google Calendar と同期対象）"""

    title = models.CharField(max_length=200, help_text="イベントタイトル")
    description = models.TextField(blank=True, help_text="イベント詳細説明")
    start_time = models.DateTimeField(help_text="イベント開始日時")
    end_time = models.DateTimeField(help_text="イベント終了日時")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
        null=True,
        blank=True,
        help_text="イベント作成者",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="events_participating",
        blank=True,
        help_text="イベント参加者",
    )

    google_event_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="Google Calendar 側のイベントID",
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="初回作成日時")
    updated_at = models.DateTimeField(auto_now=True, help_text="最終更新日時")

    def clean(self):
        """開始・終了時刻のバリデーション"""
        if self.end_time <= self.start_time:
            raise ValidationError("終了時間は開始時間より後である必要があります。")

    def __str__(self):
        return f"{self.title} [{self.start_time} - {self.end_time}] (GoogleID={self.google_event_id})"
