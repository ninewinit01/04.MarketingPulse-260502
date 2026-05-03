from datetime import datetime, timedelta

from django.core.management import call_command
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.auth import IsAdminToken

from .models import CollectionRun, ContentItem, CuratedChannel, Source, TrendKeyword
from .serializers import (
    CollectionRunSerializer,
    ContentItemSerializer,
    CuratedChannelSerializer,
    SourceSerializer,
    TrendKeywordSerializer,
)


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


class PublicContentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ContentItemSerializer

    def get_queryset(self):
        qs = ContentItem.objects.select_related("source").prefetch_related("industries")

        date = _parse_date(self.request.query_params.get("date"))
        if date:
            start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            end = start + timedelta(days=1)
            qs = qs.filter(collected_at__gte=start, collected_at__lt=end)

        industry_slug = self.request.query_params.get("industry")
        if industry_slug:
            qs = qs.filter(industries__slug=industry_slug)

        source_slug = self.request.query_params.get("source")
        if source_slug:
            qs = qs.filter(source__slug=source_slug)

        return qs.distinct()


class PublicTrendViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TrendKeywordSerializer
    pagination_class = None

    def get_queryset(self):
        qs = TrendKeyword.objects.select_related("source").prefetch_related("industries")

        date = _parse_date(self.request.query_params.get("date"))
        if date:
            start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            end = start + timedelta(days=1)
            qs = qs.filter(observed_at__gte=start, observed_at__lt=end)

        source_slug = self.request.query_params.get("source")
        if source_slug:
            qs = qs.filter(source__slug=source_slug)

        return qs


class AdminSourceViewSet(viewsets.ModelViewSet):
    serializer_class = SourceSerializer
    queryset = Source.objects.all()
    permission_classes = [IsAdminToken]
    pagination_class = None


class AdminCuratedChannelViewSet(viewsets.ModelViewSet):
    serializer_class = CuratedChannelSerializer
    queryset = CuratedChannel.objects.all()
    permission_classes = [IsAdminToken]
    pagination_class = None


class AdminCollectionRunViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CollectionRunSerializer
    permission_classes = [IsAdminToken]
    pagination_class = None

    def get_queryset(self):
        return CollectionRun.objects.select_related("source").all()[:200]

    @action(detail=False, methods=["post"])
    def trigger(self, request):
        """수동 수집 트리거. MVP에서는 동기 실행."""
        try:
            call_command("run_collection")
        except Exception as exc:
            return Response(
                {"status": "error", "message": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"status": "ok"})
