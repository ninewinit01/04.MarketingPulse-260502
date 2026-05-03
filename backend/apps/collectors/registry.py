"""Collector 레지스트리 — Source.slug → Collector 클래스 매핑."""
from __future__ import annotations

from .base import BaseCollector
from .naver_datalab import NaverDataLabCollector
from .naver_news import NaverNewsCollector
from .news_rss import NewsRSSCollector
from .youtube import YouTubeCollector
from .youtube_channels import YouTubeChannelsCollector

REGISTRY: dict[str, type[BaseCollector]] = {
    NaverNewsCollector.source_slug: NaverNewsCollector,
    NaverDataLabCollector.source_slug: NaverDataLabCollector,
    YouTubeCollector.source_slug: YouTubeCollector,
    YouTubeChannelsCollector.source_slug: YouTubeChannelsCollector,
    NewsRSSCollector.source_slug: NewsRSSCollector,
}


def get_collector_class(slug: str) -> type[BaseCollector] | None:
    return REGISTRY.get(slug)
