from .models import GoogleOAuthToken


def save_google_refresh_token(strategy, details, response, user=None, *args, **kwargs):
    """Google OAuth 認証後に refresh_token & access_token を保存"""
    refresh_token = response.get("refresh_token")
    access_token = response.get("access_token")
    client_id = response.get("client_id")
    client_secret = response.get("client_secret")
    expires_in = response.get("expires_in")

    token_data = {
        "access_token": access_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "expires_in": expires_in,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    # refresh_token が返ってきた場合のみ更新、それ以外は既存値を保持
    if refresh_token:
        token_data["refresh_token"] = refresh_token

    GoogleOAuthToken.objects.update_or_create(
        user=user,
        defaults=token_data,
    )
