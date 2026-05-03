"""네이버 뉴스 검색 API.

활성 키워드별로 24시간 내 기사 상위 10건을 가져옴.
키 없으면 mock 데이터 반환.
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from email.utils import parsedate_to_datetime

import httpx
from django.conf import settings

from apps.industries.models import Keyword

from .base import BaseCollector
from .mocks import naver_news_mock

logger = logging.getLogger(__name__)
ENDPOINT = "https://openapi.naver.com/v1/search/news.json"


def _parse_pub_date(value: str):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None


class NaverNewsCollector(BaseCollector):
    source_slug = "naver_news"

    @property
    def use_mock(self) -> bool:
        return not (settings.NAVER_CLIENT_ID and settings.NAVER_CLIENT_SECRET)

    def collect(self, run_date: date) -> list[dict]:
        if self.use_mock:
            logger.info("NaverNewsCollector: NAVER_CLIENT_ID 없음 → mock 사용")
            return naver_news_mock()

        headers = {
            "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
        }
        terms = list(
            Keyword.objects.filter(is_active=True, industry__is_active=True).values_list(
                "term", flat=True
            )
        )
        if not terms:
            logger.warning("NaverNewsCollector: 활성 키워드 없음")
            return []

        results: list[dict] = []
        seen_ids: set[str] = set()
        with httpx.Client(headers=headers, timeout=10.0) as client:
            for term in terms:
                try:
                    resp = client.get(
                        ENDPOINT,
                        params={"query": term, "display": 10, "sort": "date"},
                    )
                    resp.raise_for_status()
                except httpx.HTTPError as exc:
                    logger.warning("naver_news term=%s 실패: %s", term, exc)
                    continue

                for item in resp.json().get("items", []):
                    ext_id = item.get("originallink") or item.get("link")
                    if not ext_id or ext_id in seen_ids:
                        continue
                    seen_ids.add(ext_id)
                    title = _strip_html(item.get("title", ""))
                    desc = _strip_html(item.get("description", ""))
                    results.append(
                        {
                            "external_id": ext_id,
                            "title": title[:500],
                            "url": item.get("link") or ext_id,
                            "thumbnail_url": None,
                            "published_at": _parse_pub_date(item.get("pubDate")),
                            "raw_content": desc,
                            "metadata": {"query": term, "publisher": item.get("publisher", "")},
                        }
                    )
        return results


def _strip_html(text: str) -> str:
    return (
        text.replace("<b>", "")
        .replace("</b>", "")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&apos;", "'")
        .strip()
    )
