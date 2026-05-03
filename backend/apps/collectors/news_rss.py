"""마케팅 관련 일반 뉴스 (NewsAPI 또는 Google News RSS 폴백).

NEWSAPI_KEY 있으면 NewsAPI everything?q=마케팅..., 없으면 Google News RSS 검색.
둘 다 못 가져오면 mock.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import httpx
from django.conf import settings

from .base import BaseCollector
from .mocks import news_rss_mock

logger = logging.getLogger(__name__)

# 마케팅 토픽 검색 쿼리 (Google News + NewsAPI 공통)
MARKETING_QUERY = (
    "마케팅 OR 광고 OR 브랜드 OR 트렌드 OR 캠페인 OR 인플루언서 "
    "OR SNS OR 콘텐츠 OR 소비자 OR 이커머스 OR 스타트업"
)

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"
GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    f"?q={quote(MARKETING_QUERY)}+when:1d&hl=ko&gl=KR&ceid=KR:ko"
)


def _parse_dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None


class NewsRSSCollector(BaseCollector):
    source_slug = "newsapi"

    @property
    def use_mock(self) -> bool:
        return False  # RSS 폴백이 있으므로 항상 시도

    def collect(self, run_date: date) -> list[dict]:
        # 1순위: Google News RSS 검색 (마케팅 토픽으로 좁힌 결과 — 정확도 가장 높음)
        try:
            items = self._collect_rss()
            if items:
                return items
        except (httpx.HTTPError, ET.ParseError) as exc:
            logger.warning("RSS 실패: %s", exc)

        # 2순위: NewsAPI everything (RSS 실패 시만)
        if settings.NEWSAPI_KEY:
            try:
                items = self._collect_newsapi()
                if items:
                    return items
            except httpx.HTTPError as exc:
                logger.warning("NewsAPI 실패: %s", exc)

        logger.info("NewsRSSCollector: mock 사용")
        return news_rss_mock()

    def _collect_newsapi(self) -> list[dict]:
        from_dt = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        resp = httpx.get(
            NEWSAPI_ENDPOINT,
            params={
                "q": MARKETING_QUERY,
                "language": "ko",
                "from": from_dt,
                "sortBy": "publishedAt",
                "pageSize": 30,
                "apiKey": settings.NEWSAPI_KEY,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        results = []
        for art in resp.json().get("articles", []):
            url = art.get("url")
            if not url:
                continue
            results.append(
                {
                    "external_id": url,
                    "title": (art.get("title") or "")[:500],
                    "url": url,
                    "thumbnail_url": art.get("urlToImage"),
                    "published_at": _parse_dt(art.get("publishedAt")),
                    "raw_content": art.get("description") or "",
                    "metadata": {"source": (art.get("source") or {}).get("name", "")},
                }
            )
        return results

    def _collect_rss(self) -> list[dict]:
        resp = httpx.get(GOOGLE_NEWS_RSS, timeout=10.0, follow_redirects=True)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        channel = root.find("channel")
        if channel is None:
            return []
        results = []
        for item in channel.findall("item")[:20]:
            link = (item.findtext("link") or "").strip()
            if not link:
                continue
            results.append(
                {
                    "external_id": link,
                    "title": (item.findtext("title") or "")[:500],
                    "url": link,
                    "thumbnail_url": None,
                    "published_at": _parse_dt(item.findtext("pubDate")),
                    "raw_content": item.findtext("description") or "",
                    "metadata": {"source": (item.findtext("source") or "Google News")},
                }
            )
        return results
