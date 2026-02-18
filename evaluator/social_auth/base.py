"""Abstract base classes for OAuth providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SocialUserInfo:
    provider: str
    provider_id: str
    nickname: str
    profile_image_url: str
    email: str = ""


class OAuthProvider(ABC):
    name: str

    @abstractmethod
    def build_authorization_url(self, redirect_uri: str, state: str) -> str: ...

    @abstractmethod
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict: ...

    @abstractmethod
    def fetch_user_profile(self, access_token: str) -> SocialUserInfo: ...
