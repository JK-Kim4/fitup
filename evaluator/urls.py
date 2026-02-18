"""URL configuration for the evaluator app."""

from django.urls import path

from .auth_views import GenericCallbackView, GenericLoginView, LogoutView
from .views import EvaluationView

app_name = "evaluator"

urlpatterns = [
    path("", EvaluationView.as_view(), name="index"),
    path("auth/<str:provider>/login/", GenericLoginView.as_view(), name="social_login"),
    path("auth/<str:provider>/callback/", GenericCallbackView.as_view(), name="social_callback"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
