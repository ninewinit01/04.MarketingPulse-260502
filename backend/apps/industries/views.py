from rest_framework import mixins, viewsets

from apps.core.auth import IsAdminToken

from .models import Industry, Keyword
from .serializers import IndustrySerializer, KeywordSerializer


class PublicIndustryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """공개 — 활성 업종 목록만 반환."""

    serializer_class = IndustrySerializer
    queryset = Industry.objects.filter(is_active=True)
    pagination_class = None


class AdminIndustryViewSet(viewsets.ModelViewSet):
    serializer_class = IndustrySerializer
    queryset = Industry.objects.all()
    permission_classes = [IsAdminToken]
    pagination_class = None


class AdminKeywordViewSet(viewsets.ModelViewSet):
    serializer_class = KeywordSerializer
    queryset = Keyword.objects.select_related("industry").all()
    permission_classes = [IsAdminToken]
    filterset_fields = ["industry", "is_active"]
    pagination_class = None
