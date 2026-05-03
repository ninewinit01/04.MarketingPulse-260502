from rest_framework import serializers

from apps.industries.models import Industry

from .models import CollectionRun, ContentItem, CuratedChannel, Source, TrendKeyword


class CuratedChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuratedChannel
        fields = ("id", "name", "handle", "description", "is_active", "created_at")
        read_only_fields = ("created_at",)


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ("id", "name", "slug", "type", "is_active")


class _IndustryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ("id", "name", "slug")


class ContentItemSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    industries = _IndustryMiniSerializer(many=True, read_only=True)

    class Meta:
        model = ContentItem
        fields = (
            "id",
            "source",
            "external_id",
            "title",
            "url",
            "thumbnail_url",
            "published_at",
            "collected_at",
            "metadata",
            "industries",
            "is_pinned",
            "llm_summary",
        )


class TrendKeywordSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    industries = _IndustryMiniSerializer(many=True, read_only=True)

    class Meta:
        model = TrendKeyword
        fields = ("id", "source", "keyword", "rank", "observed_at", "metadata", "industries")


class CollectionRunSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    duration_ms = serializers.SerializerMethodField()

    class Meta:
        model = CollectionRun
        fields = (
            "id",
            "source",
            "started_at",
            "finished_at",
            "status",
            "error_message",
            "items_collected",
            "duration_ms",
        )

    def get_duration_ms(self, obj):
        if obj.started_at and obj.finished_at:
            return int((obj.finished_at - obj.started_at).total_seconds() * 1000)
        return None
