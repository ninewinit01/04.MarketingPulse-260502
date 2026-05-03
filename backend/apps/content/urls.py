from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminCollectionRunViewSet,
    AdminCuratedChannelViewSet,
    AdminSourceViewSet,
    PublicContentViewSet,
    PublicTrendViewSet,
)

public_router = DefaultRouter()
public_router.register(r"content", PublicContentViewSet, basename="content")
public_router.register(r"trends", PublicTrendViewSet, basename="trends")

admin_router = DefaultRouter()
admin_router.register(r"sources", AdminSourceViewSet, basename="admin-sources")
admin_router.register(r"channels", AdminCuratedChannelViewSet, basename="admin-channels")
admin_router.register(r"runs", AdminCollectionRunViewSet, basename="admin-runs")

urlpatterns = [
    path("", include(public_router.urls)),
    path("admin/", include(admin_router.urls)),
]
