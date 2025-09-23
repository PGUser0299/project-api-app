from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class GoogleOAuthToken(models.Model):
    """
    Google OAuth 認証情報を保存
    - access_token は常に存在するとは限らないので nullable
    - refresh_token は必須（再取得に必要）
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="google_oauth_token"
    )
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField()
    token_uri = models.CharField(
        max_length=255,
        default="https://oauth2.googleapis.com/token"
    )
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    expiry = models.DateTimeField(blank=True, null=True)
    expires_in = models.IntegerField(blank=True, null=True)
    id_token = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google OAuth Token for {self.user.username}"


class CalendarEvent(models.Model):
    """
    Google カレンダーと同期されるイベント情報
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
        null=True,
        blank=True
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="events_participating",
        blank=True
    )
    google_event_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"
