"""URL routes for the WASA dashboard."""
from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("dashboard.urls")),
]
