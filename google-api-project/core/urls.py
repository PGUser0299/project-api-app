from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
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
    path("api/", include("api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="api-schema"), name="redoc"),
]
