from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/", include("apps.industries.urls")),
    path("api/", include("apps.content.urls")),
    path("api/", include("apps.dashboard.urls")),
]
