"""Dashboard page routes."""
from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("", views.overview, name="overview"),
    path("overview/", views.overview, name="overview"),
    path("demographics/", views.demographics, name="demographics"),
    path("production/", views.production, name="production"),
    path("adoption/", views.adoption, name="adoption"),
    path("recommendations/", views.recommendations, name="recommendations"),
]
