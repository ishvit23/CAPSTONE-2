import logging
import secrets
from urllib.parse import urlencode, quote

import requests
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .services.mongo_client import mongo_db as get_mongo_db

logger = logging.getLogger(__name__)

GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_SCOPES = "openid email profile"

signer = TimestampSigner()
User = get_user_model()


class GoogleAuthInitView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            return Response(
                {"error": "Google OAuth is not configured on the server."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        state_payload = secrets.token_urlsafe(16)
        state = signer.sign(state_payload)
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": GOOGLE_SCOPES,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        auth_url = f"{GOOGLE_AUTH_BASE}?{urlencode(params)}"
        return Response({"auth_url": auth_url})


class GoogleAuthCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")

        if error:
            logger.error("Google OAuth error: %s", error)
            return self._redirect_with_error("google_auth_failed")

        if not code or not state:
            return self._redirect_with_error("missing_code_or_state")

        try:
            signer.unsign(state, max_age=300)
        except SignatureExpired:
            return self._redirect_with_error("state_expired")
        except BadSignature:
            return self._redirect_with_error("invalid_state")

        token_payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_payload, timeout=10)
        if token_response.status_code != 200:
            logger.error(
                "Failed to exchange auth code: %s", token_response.text[:200]
            )
            return self._redirect_with_error("token_exchange_failed")

        token_data = token_response.json()
        google_access_token = token_data.get("access_token")

        if not google_access_token:
            return self._redirect_with_error("missing_google_access_token")

        userinfo_response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"},
            timeout=10,
        )
        if userinfo_response.status_code != 200:
            logger.error("Failed to fetch Google userinfo: %s", userinfo_response.text)
            return self._redirect_with_error("userinfo_failed")

        userinfo = userinfo_response.json()
        email = userinfo.get("email")
        name = userinfo.get("name") or ""

        if not email:
            return self._redirect_with_error("email_not_provided")

        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0]},
        )
        first_name, *rest = name.split(" ", 1)
        user.first_name = first_name
        if rest:
            user.last_name = rest[0]
        user.save()

        get_mongo_db().users.update_one(
            {"email": email},
            {
                "$set": {
                    "email": email,
                    "google_id": userinfo.get("id"),
                    "name": name,
                    "picture": userinfo.get("picture"),
                    "locale": userinfo.get("locale"),
                    "last_login": timezone.now(),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            },
            upsert=True,
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        frontend_redirect = (
            f"{settings.FRONTEND_APP_URL}/auth/callback"
            f"?access={quote(access_token)}"
            f"&refresh={quote(refresh_token)}"
        )
        return HttpResponseRedirect(frontend_redirect)

    @staticmethod
    def _redirect_with_error(error_code: str):
        redirect_url = f"{settings.FRONTEND_APP_URL}/auth/callback?error={quote(error_code)}"
        return HttpResponseRedirect(redirect_url)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
            }
        )

