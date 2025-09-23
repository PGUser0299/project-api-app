import os
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .models import GoogleOAuthToken, CalendarEvent
from .serializers import CalendarEventSerializer
from .tasks import (
    create_google_calendar_event,
    update_google_calendar_event,
    delete_google_calendar_event,
)

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def test_google_api(request):
    """ユーザーの Gmail API プロフィールを取得"""
    user = request.user
    try:
        token_obj = GoogleOAuthToken.objects.get(user=user)
    except GoogleOAuthToken.DoesNotExist:
        return Response({"error": "No Google token found"}, status=400)

    creds = Credentials(
        token=token_obj.access_token,
        refresh_token=token_obj.refresh_token,
        token_uri=token_obj.token_uri,
        client_id=token_obj.client_id,
        client_secret=token_obj.client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )

    if not creds.valid and creds.refresh_token:
        creds.refresh(requests.Request())

    try:
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        return Response({"emailAddress": profile["emailAddress"]})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def account(request):
    """ログイン中のユーザー情報を返す"""
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login_jwt(request):
    """Google の ID Token を検証して JWT を発行"""
    token = request.data.get("id_token")
    if not token:
        return Response({"error": "id_token is required"}, status=400)

    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_OAUTH2_CLIENT_ID,
        )
    except Exception:
        return Response({"error": "Invalid Google token"}, status=400)

    email = payload.get("email")
    if not email:
        return Response({"error": "Email not available"}, status=400)

    user, _ = User.objects.get_or_create(username=email, defaults={"email": email})
    refresh = RefreshToken.for_user(user)

    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """JWT のログアウト (トークンブラックリスト化)"""
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out"}, status=200)
    except Exception:
        return Response({"error": "Invalid token"}, status=400)


class CalendarEventViewSet(viewsets.ModelViewSet):
    """Google カレンダーと同期するイベント管理 ViewSet"""

    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        event = serializer.save(created_by=self.request.user)
        create_google_calendar_event.delay(event.id, self.request.user.id)

    def perform_update(self, serializer):
        event = serializer.save()
        update_google_calendar_event.delay(event.id, self.request.user.id)

    def perform_destroy(self, instance):
        user = self.request.user
        google_event_id = instance.google_event_id
        delete_google_calendar_event.delay(instance.id, user.id, google_event_id)
        instance.delete()


class GoogleLoginView(APIView):
    """Google ログイン + トークン保存"""

    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("id_token")
        access_token = request.data.get("access_token")
        refresh_token = request.data.get("refresh_token")
        expires_in = request.data.get("expires_in")

        if not token:
            return Response({"error": "id_token required"}, status=400)

        try:
            client_id = getattr(
                settings,
                "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY",
                os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"),
            )
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

            email = idinfo.get("email")
            user, _ = User.objects.get_or_create(username=email, defaults={"email": email})

            if refresh_token:
                GoogleOAuthToken.objects.update_or_create(
                    user=user,
                    defaults={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_in": expires_in,
                        "client_id": client_id,
                        "client_secret": os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"),
                        "token_uri": "https://oauth2.googleapis.com/token",
                    },
                )

            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            })
        except ValueError:
            return Response({"error": "Invalid token"}, status=400)


class SaveGoogleTokenView(APIView):
    """アクセストークン・リフレッシュトークンを保存"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        access_token = request.data.get("access_token")
        refresh_token = request.data.get("refresh_token")
        expires_in = request.data.get("expires_in")

        if not refresh_token:
            return Response({"error": "refresh_token required"}, status=400)

        token_obj, created = GoogleOAuthToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
                "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                "token_uri": "https://oauth2.googleapis.com/token",
            },
        )
        return Response({
            "status": "saved",
            "created": created,
            "user": user.username,
        })
