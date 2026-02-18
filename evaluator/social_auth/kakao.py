"""Kakao OAuth2 provider implementation."""

import urllib.parse

import requests
from django.conf import settings

from .base import OAuthProvider, SocialUserInfo


class KakaoOAuthProvider(OAuthProvider):
    name = "kakao"
    AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
    TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    PROFILE_URL = "https://kapi.kakao.com/v2/user/me"

    def build_authorization_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        resp = requests.post(self.TOKEN_URL, data=data, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def fetch_user_profile(self, access_token: str) -> SocialUserInfo:
        resp = requests.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        account = data.get("kakao_account", {})
        profile = account.get("profile", {})
        return SocialUserInfo(
            provider="kakao",
            provider_id=str(data["id"]),
            nickname=profile.get("nickname", ""),
            profile_image_url=profile.get("profile_image_url", ""),
            email=account.get("email", ""),
        )
