from django.contrib import admin

from .models import AnalysisHistory, RequestLog, SocialProfile


@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = ("provider", "provider_id", "nickname", "user", "connected_at")
    list_filter = ("provider",)
    search_fields = ("provider_id", "nickname", "user__username")
    readonly_fields = ("connected_at",)


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "user", "requested_at")
    list_filter = ("requested_at",)
    search_fields = ("ip_address", "user__username")
    readonly_fields = ("requested_at",)


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ("requested_at", "provider", "user", "ip_address", "resume_filename")
    list_filter = ("provider", "requested_at")
    search_fields = ("ip_address", "user__username", "resume_filename")
    readonly_fields = ("requested_at",)
    date_hierarchy = "requested_at"
