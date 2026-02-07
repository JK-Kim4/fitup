"""URL configuration for the evaluator app."""

from django.urls import path

from .views import EvaluationView

app_name = "evaluator"

urlpatterns = [
    path("", EvaluationView.as_view(), name="index"),
]
