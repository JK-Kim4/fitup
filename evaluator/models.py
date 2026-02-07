from django.db import models
from django.utils import timezone


class RequestLog(models.Model):
    """IP별 요청 기록을 저장하는 모델."""

    ip_address = models.GenericIPAddressField(verbose_name="IP 주소")
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="요청 시간")

    class Meta:
        verbose_name = "요청 기록"
        verbose_name_plural = "요청 기록"
        indexes = [
            models.Index(fields=["ip_address", "requested_at"]),
        ]

    def __str__(self):
        return f"{self.ip_address} - {self.requested_at}"

    @classmethod
    def get_today_count(cls, ip_address: str) -> int:
        """오늘 해당 IP의 요청 횟수를 반환합니다."""
        today = timezone.now().date()
        return cls.objects.filter(
            ip_address=ip_address,
            requested_at__date=today
        ).count()

    @classmethod
    def can_make_request(cls, ip_address: str, daily_limit: int = 3) -> bool:
        """해당 IP가 요청 가능한지 확인합니다."""
        return cls.get_today_count(ip_address) < daily_limit

    @classmethod
    def log_request(cls, ip_address: str) -> "RequestLog":
        """요청을 기록합니다."""
        return cls.objects.create(ip_address=ip_address)

    @classmethod
    def get_remaining_requests(cls, ip_address: str, daily_limit: int = 3) -> int:
        """남은 요청 횟수를 반환합니다."""
        return max(0, daily_limit - cls.get_today_count(ip_address))
