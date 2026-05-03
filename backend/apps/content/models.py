from django.db import models

from apps.industries.models import Industry


class Source(models.Model):
    class Type(models.TextChoices):
        NEWS = "news", "뉴스"
        VIDEO = "video", "동영상"
        SEARCH_TREND = "search_trend", "검색 트렌드"
        SNS = "sns", "SNS"

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=80, unique=True)
    type = models.CharField(max_length=20, choices=Type.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ContentItem(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="items")
    external_id = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    url = models.CharField(max_length=1000)
    thumbnail_url = models.CharField(max_length=1000, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)
    raw_content = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    industries = models.ManyToManyField(Industry, blank=True, related_name="items")
    is_pinned = models.BooleanField(default=False)
    llm_summary = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("-published_at", "-collected_at")
        indexes = [
            models.Index(fields=["published_at"]),
            models.Index(fields=["collected_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"], name="uniq_source_external_id"
            ),
        ]

    def __str__(self):
        return self.title[:80]


class TrendKeyword(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="trends")
    keyword = models.CharField(max_length=120)
    rank = models.IntegerField()
    observed_at = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)
    industries = models.ManyToManyField(Industry, blank=True, related_name="trends")

    class Meta:
        ordering = ("rank",)
        indexes = [
            models.Index(fields=["observed_at", "source"]),
        ]

    def __str__(self):
        return f"#{self.rank} {self.keyword} ({self.source.slug})"


class CuratedChannel(models.Model):
    """YouTube 큐레이션 채널 — Admin에서 관리, youtube_channels collector가 사용."""

    name = models.CharField(max_length=120, blank=True, help_text="표시용. 비우면 채널 메타에서 가져옴.")
    handle = models.CharField(
        max_length=120,
        unique=True,
        help_text="@핸들 (예: @sebasi15) 또는 channel ID (예: UCxxxxxx).",
    )
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-is_active", "name", "id")

    def __str__(self):
        return f"{self.name or self.handle} ({self.handle})"


class CollectionRun(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "성공"
        PARTIAL = "partial", "부분 성공"
        FAILED = "failed", "실패"
        RUNNING = "running", "실행 중"

    source = models.ForeignKey(
        Source, on_delete=models.SET_NULL, null=True, blank=True, related_name="runs"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)
    error_message = models.TextField(blank=True)
    items_collected = models.IntegerField(default=0)

    class Meta:
        ordering = ("-started_at",)

    def __str__(self):
        src = self.source.slug if self.source else "all"
        return f"{src} @ {self.started_at:%Y-%m-%d %H:%M} [{self.status}]"
