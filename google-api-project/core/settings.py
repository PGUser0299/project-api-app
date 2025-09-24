from pathlib import Path, os
from decouple import config
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent

# セキュリティ設定
SECRET_KEY = config("SECRET_KEY", default="dummy-secret-key")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = ["localhost",]

# アプリケーション定義
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "social_django",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# データベース
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "google_api_db",
        "USER": "api-user",
        "PASSWORD": "api-1234",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

# パスワード検証
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ロケール設定
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# 静的ファイル
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 認証
AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

# REST Framework 設定
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# JWT 設定
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

# Google OAuth 設定
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/api/account/"
LOGOUT_REDIRECT_URL = "/"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", default=None)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", default=None)
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["email", "profile"]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ["first_name", "last_name"]

GOOGLE_OAUTH2_CLIENT_ID = config("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", default=None)
GOOGLE_CLIENT_ID = config("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", default=None)
GOOGLE_CLIENT_SECRET = config("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", default=None)
GOOGLE_TOKEN_URI = config("GOOGLE_TOKEN_URI")

# Celery 設定
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tokyo"

# Social Auth Pipeline (Google Refresh Token 保存用)
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "api.pipelines.save_google_refresh_token",
)
