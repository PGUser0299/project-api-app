from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CalendarEventViewSet,
    GoogleLoginView,
    SaveGoogleTokenView,
    test_google_api,
    account,
    google_login_jwt,
    logout,
)


router = DefaultRouter()
router.register(r"events", CalendarEventViewSet, basename="calendar-event")

urlpatterns = [
    path("auth/google/login/", GoogleLoginView.as_view(), name="google-login"),
    path("auth/google/save-token/", SaveGoogleTokenView.as_view(), name="save-google-token"),
    path("auth/google/test/", test_google_api, name="test-google-api"),
    path("auth/google/jwt/", google_login_jwt, name="google-login-jwt"),
    path("auth/logout/", logout, name="logout"),
    path("auth/account/", account, name="account"),
    path("", include(router.urls)),
]
