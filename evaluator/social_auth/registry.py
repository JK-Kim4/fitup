"""OAuth provider registry."""

from .base import OAuthProvider
from .kakao import KakaoOAuthProvider

PROVIDERS: dict[str, OAuthProvider] = {
    "kakao": KakaoOAuthProvider(),
    # "google": GoogleOAuthProvider(),
    # "naver": NaverOAuthProvider(),
}


def get_provider(name: str) -> OAuthProvider:
    if name not in PROVIDERS:
        raise ValueError(f"Unknown OAuth provider: {name}")
    return PROVIDERS[name]
