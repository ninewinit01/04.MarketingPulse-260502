"""YouTube Data API v3 — 마케팅 영상 수집.

A. "마케팅" 키워드 단일 검색으로 viewCount 정렬 → 마케팅 인기 영상 (최근 7일)
B. 업종별 대표 키워드 1개씩 검색 → 업종 카드용 영상 (조회수 정렬)

quota: 1 (A) + 5 (B) = 600 quota / 회. 일 한도 10,000 안에서 안전.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone

import httpx
from django.conf import settings

from apps.industries.models import Industry

from .base import BaseCollector
from .mocks import youtube_mock

logger = logging.getLogger(__name__)
SEARCH_ENDPOINT = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"

# A. 마케팅 토픽 검색 — 단일 단어는 noise 많음. 두 단어 phrase 조합으로 좁힘.
MARKETING_QUERY = (
    '"마케팅 사례" OR "마케팅 트렌드" OR "브랜드 마케팅" OR "광고 분석" '
    'OR "퍼포먼스 마케팅" OR "콘텐츠 마케팅" OR "마케팅 전략"'
)

# B. 업종 slug → 검색 키워드 (단순 두 단어, phrase는 결과 너무 좁음)
INDUSTRY_REPRESENTATIVE_KW: dict[str, str] = {
    "legal": "변호사 마케팅",
    "hospital": "병원 마케팅",
    "fashion": "패션 브랜드 마케팅",
    "lodging": "호텔 마케팅",
    "restaurant": "외식업 마케팅",
}

A_RESULTS = 20
B_RESULTS = 5


def _parse_dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class YouTubeCollector(BaseCollector):
    source_slug = "youtube"

    @property
    def use_mock(self) -> bool:
        return not settings.YOUTUBE_API_KEY

    def collect(self, run_date: date) -> list[dict]:
        if self.use_mock:
            logger.info("YouTubeCollector: YOUTUBE_API_KEY 없음 → mock")
            return youtube_mock()

        api_key = settings.YOUTUBE_API_KEY
        published_after = (
            datetime.now(timezone.utc) - timedelta(days=7)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        results: list[dict] = []
        seen: set[str] = set()

        with httpx.Client(timeout=10.0) as client:
            # A. 마케팅 토픽 인기 영상
            try:
                resp = client.get(
                    SEARCH_ENDPOINT,
                    params={
                        "part": "snippet",
                        "q": MARKETING_QUERY,
                        "type": "video",
                        "regionCode": "KR",
                        "relevanceLanguage": "ko",
                        "order": "viewCount",
                        "publishedAfter": published_after,
                        "maxResults": A_RESULTS,
                        "key": api_key,
                    },
                )
                resp.raise_for_status()
                for item in resp.json().get("items", []):
                    vid = item.get("id", {}).get("videoId")
                    if not vid or vid in seen:
                        continue
                    seen.add(vid)
                    snippet = item.get("snippet", {})
                    results.append(_yt_item(vid, snippet, kind="marketing_top"))
            except httpx.HTTPError as exc:
                logger.warning("youtube A (marketing) 실패: %s", exc)

            # B. 업종별 대표 키워드 검색
            for industry in Industry.objects.filter(is_active=True):
                kw = INDUSTRY_REPRESENTATIVE_KW.get(industry.slug)
                if not kw:
                    continue
                try:
                    resp = client.get(
                        SEARCH_ENDPOINT,
                        params={
                            "part": "snippet",
                            "q": kw,
                            "type": "video",
                            "regionCode": "KR",
                            "relevanceLanguage": "ko",
                            "order": "viewCount",
                            "publishedAfter": published_after,
                            "maxResults": B_RESULTS,
                            "key": api_key,
                        },
                    )
                    resp.raise_for_status()
                    for item in resp.json().get("items", []):
                        vid = item.get("id", {}).get("videoId")
                        if not vid or vid in seen:
                            continue
                        seen.add(vid)
                        snippet = item.get("snippet", {})
                        results.append(
                            _yt_item(
                                vid,
                                snippet,
                                kind="industry",
                                industry_slug=industry.slug,
                                industry_name=industry.name,
                                query=kw,
                            )
                        )
                except httpx.HTTPError as exc:
                    logger.warning("youtube B (%s/%s) 실패: %s", industry.slug, kw, exc)

        return results


def _yt_item(
    vid: str,
    snippet: dict,
    kind: str,
    industry_slug: str | None = None,
    industry_name: str | None = None,
    query: str | None = None,
) -> dict:
    thumbs = snippet.get("thumbnails", {})
    thumb = (thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}).get("url")
    return {
        "external_id": vid,
        "title": (snippet.get("title") or "")[:500],
        "url": f"https://www.youtube.com/watch?v={vid}",
        "thumbnail_url": thumb,
        "published_at": _parse_dt(snippet.get("publishedAt")),
        "raw_content": snippet.get("description") or "",
        "metadata": {
            "channel": snippet.get("channelTitle"),
            "_kind": kind,
            "industry_slug": industry_slug,
            "industry_name": industry_name,
            "query": query,
        },
    }
