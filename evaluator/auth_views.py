"""Generic OAuth2 authentication views."""

import secrets

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from .models import SocialProfile
from .social_auth.registry import get_provider


class GenericLoginView(View):
    def get(self, request, provider):
        try:
            p = get_provider(provider)
        except ValueError:
            raise Http404

        state = secrets.token_urlsafe(32)
        request.session["oauth_state"] = state
        request.session["oauth_provider"] = provider

        redirect_uri = request.build_absolute_uri(
            reverse("evaluator:social_callback", kwargs={"provider": provider})
        )
        return redirect(p.build_authorization_url(redirect_uri, state))


class GenericCallbackView(View):
    def get(self, request, provider):
        try:
            p = get_provider(provider)
        except ValueError:
            raise Http404

        # 1. state CSRF 검증
        state = request.GET.get("state", "")
        session_state = request.session.pop("oauth_state", None)
        if not session_state or state != session_state:
            return redirect(reverse("evaluator:index") + "?auth_error=invalid_state")

        # 2. 에러 처리
        error = request.GET.get("error")
        if error:
            return redirect(reverse("evaluator:index") + f"?auth_error={error}")

        code = request.GET.get("code")
        if not code:
            return redirect(reverse("evaluator:index") + "?auth_error=no_code")

        # 3. 토큰 교환
        redirect_uri = request.build_absolute_uri(
            reverse("evaluator:social_callback", kwargs={"provider": provider})
        )
        try:
            token_data = p.exchange_code_for_token(code, redirect_uri)
        except Exception:
            return redirect(reverse("evaluator:index") + "?auth_error=token_exchange_failed")

        access_token = token_data.get("access_token")
        if not access_token:
            return redirect(reverse("evaluator:index") + "?auth_error=no_access_token")

        # 4. 프로필 조회
        try:
            user_info = p.fetch_user_profile(access_token)
        except Exception:
            return redirect(reverse("evaluator:index") + "?auth_error=profile_fetch_failed")

        # 5. SocialProfile 기반 User get-or-create
        social_profile = SocialProfile.objects.filter(
            provider=user_info.provider,
            provider_id=user_info.provider_id,
        ).select_related("user").first()

        if social_profile:
            user = social_profile.user
            # 닉네임/이미지 업데이트
            social_profile.nickname = user_info.nickname
            social_profile.profile_image_url = user_info.profile_image_url
            social_profile.save(update_fields=["nickname", "profile_image_url"])
        else:
            # 신규 사용자 생성
            username = f"{user_info.provider}_{user_info.provider_id}"
            user, _ = User.objects.get_or_create(username=username)
            if user_info.email:
                user.email = user_info.email
                user.save(update_fields=["email"])
            SocialProfile.objects.create(
                user=user,
                provider=user_info.provider,
                provider_id=user_info.provider_id,
                nickname=user_info.nickname,
                profile_image_url=user_info.profile_image_url,
            )

        # 6. login() 호출
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        # 7. 메인 페이지 리다이렉트
        return redirect(reverse("evaluator:index"))


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(reverse("evaluator:index"))
