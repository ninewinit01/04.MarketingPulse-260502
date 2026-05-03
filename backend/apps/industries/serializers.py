from rest_framework import serializers

from .models import Industry, Keyword


class IndustrySerializer(serializers.ModelSerializer):
    keyword_count = serializers.IntegerField(source="keywords.count", read_only=True)

    class Meta:
        model = Industry
        fields = ("id", "name", "slug", "is_active", "sort_order", "keyword_count", "created_at")
        read_only_fields = ("created_at", "keyword_count")


class KeywordSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source="industry.name", read_only=True)

    class Meta:
        model = Keyword
        fields = ("id", "industry", "industry_name", "term", "weight", "is_active")
