from django.urls import path
from django.http import JsonResponse
from .app import analyze_async, analysis_status, health

urlpatterns = [
    path("health/", health),
    path("analysis/async", analyze_async),
    path("status/<str:task_id>/", analysis_status),
]
