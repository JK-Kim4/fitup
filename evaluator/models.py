from django.conf import settings
from django.db import models
from django.utils import timezone


class SocialProfile(models.Model):
    """소셜 로그인 프로필 모델 (다중 Provider 지원)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_profiles",
    )
    provider = models.CharField(max_length=50)
    provider_id = models.CharField(max_length=200)
    nickname = models.CharField(max_length=100, blank=True)
    profile_image_url = models.URLField(blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "소셜 프로필"
        verbose_name_plural = "소셜 프로필"
        unique_together = [("provider", "provider_id")]
        indexes = [models.Index(fields=["provider", "provider_id"])]

    def __str__(self):
        return f"{self.provider}:{self.provider_id} ({self.user})"


class RequestLog(models.Model):
    """IP별/유저별 요청 기록을 저장하는 모델."""

    ip_address = models.GenericIPAddressField(verbose_name="IP 주소")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_logs",
        verbose_name="사용자",
    )
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="요청 시간")

    ANONYMOUS_DAILY_LIMIT = 1
    USER_DAILY_LIMIT = 3

    class Meta:
        verbose_name = "요청 기록"
        verbose_name_plural = "요청 기록"
        indexes = [
            models.Index(fields=["ip_address", "requested_at"]),
            models.Index(fields=["user", "requested_at"]),
        ]

    def __str__(self):
        return f"{self.ip_address} - {self.requested_at}"

    @classmethod
    def get_today_count(cls, ip_address: str, user=None) -> int:
        """오늘 해당 IP 또는 유저의 요청 횟수를 반환합니다."""
        today = timezone.now().date()
        if user and user.is_authenticated:
            return cls.objects.filter(user=user, requested_at__date=today).count()
        return cls.objects.filter(ip_address=ip_address, requested_at__date=today).count()

    @classmethod
    def get_daily_limit(cls, user=None) -> int:
        """일일 요청 한도를 반환합니다."""
        if user and user.is_authenticated:
            return cls.USER_DAILY_LIMIT
        return cls.ANONYMOUS_DAILY_LIMIT

    @classmethod
    def can_make_request(cls, ip_address: str, user=None) -> bool:
        """해당 IP/유저가 요청 가능한지 확인합니다."""
        limit = cls.get_daily_limit(user)
        return cls.get_today_count(ip_address, user) < limit

    @classmethod
    def log_request(cls, ip_address: str, user=None) -> "RequestLog":
        """요청을 기록합니다."""
        return cls.objects.create(
            ip_address=ip_address,
            user=user if (user and user.is_authenticated) else None,
        )

    @classmethod
    def get_remaining_requests(cls, ip_address: str, user=None) -> int:
        """남은 요청 횟수를 반환합니다."""
        limit = cls.get_daily_limit(user)
        return max(0, limit - cls.get_today_count(ip_address, user))


class AnalysisHistory(models.Model):
    """분석 요청 이력을 저장하는 모델."""

    ip_address = models.GenericIPAddressField(verbose_name="IP 주소")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analysis_histories",
        verbose_name="사용자",
    )
    provider = models.CharField(max_length=50, verbose_name="AI 모델")
    resume_filename = models.CharField(max_length=255, blank=True, verbose_name="이력서 파일명")
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="요청 일시")

    class Meta:
        verbose_name = "분석 이력"
        verbose_name_plural = "분석 이력"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["user", "requested_at"]),
            models.Index(fields=["ip_address", "requested_at"]),
        ]

    def __str__(self):
        who = str(self.user) if self.user else self.ip_address
        return f"{who} | {self.provider} | {self.requested_at:%Y-%m-%d %H:%M}"
