from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminIndustryViewSet, AdminKeywordViewSet, PublicIndustryViewSet

public_router = DefaultRouter()
public_router.register(r"industries", PublicIndustryViewSet, basename="industries")

admin_router = DefaultRouter()
admin_router.register(r"industries", AdminIndustryViewSet, basename="admin-industries")
admin_router.register(r"keywords", AdminKeywordViewSet, basename="admin-keywords")

urlpatterns = [
    path("", include(public_router.urls)),
    path("admin/", include(admin_router.urls)),
]
