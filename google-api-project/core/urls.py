from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/jwt/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/jwt/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/jwt/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/", include("calendarapp.urls")),
]
