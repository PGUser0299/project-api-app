from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CalendarEvent, GoogleOAuthToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報シリアライズ"""
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CalendarEventSerializer(serializers.ModelSerializer):
    """カレンダーイベントシリアライズ"""
    created_by = serializers.ReadOnlyField(source="created_by.username")
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
    )
    participants_detail = UserSerializer(
        many=True,
        read_only=True,
        source="participants",
    )

    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "created_by",
            "participants",
            "participants_detail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by"]

    def validate(self, data):
        """開始時間と終了時間の整合性チェック"""
        start_time = data.get("start_time", getattr(self.instance, "start_time", None))
        end_time = data.get("end_time", getattr(self.instance, "end_time", None))

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("終了時間は開始時間より後である必要があります。")
        return data


class GoogleOAuthTokenSerializer(serializers.ModelSerializer):
    """Google OAuth トークンシリアライズ"""
    class Meta:
        model = GoogleOAuthToken
        fields = [
            "access_token",
            "refresh_token",
            "expires_in",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
