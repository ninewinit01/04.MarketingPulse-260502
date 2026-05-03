"""마케팅/비즈니스 큐레이션 유튜브 채널의 최신 영상.

CHANNEL_HANDLES에 등록된 채널들의 uploads playlist에서 최근 N개 영상 수집.
quota: 채널당 forHandle 조회 1 + playlistItems 1 ≈ 2.

핸들이 변경되거나 채널이 없으면 그 채널만 skip.
"""
from __future__ import annotations

import logging
from datetime import date, datetime

import httpx
from django.conf import settings

from .base import BaseCollector
from .mocks import youtube_channels_mock

logger = logging.getLogger(__name__)

CHANNELS_ENDPOINT = "https://www.googleapis.com/youtube/v3/channels"
PLAYLIST_ITEMS_ENDPOINT = "https://www.googleapis.com/youtube/v3/playlistItems"

# 큐레이션 채널은 DB의 CuratedChannel 모델에서 관리 (Admin UI에서 추가/삭제).
# 하나도 없으면 빈 결과 반환.

ITEMS_PER_CHANNEL = 3


def _parse_dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class YouTubeChannelsCollector(BaseCollector):
    source_slug = "youtube_channels"

    @property
    def use_mock(self) -> bool:
        return not settings.YOUTUBE_API_KEY

    def collect(self, run_date: date) -> list[dict]:
        if self.use_mock:
            logger.info("YouTubeChannelsCollector: YOUTUBE_API_KEY 없음 → mock")
            return youtube_channels_mock()

        from apps.content.models import CuratedChannel

        handles = list(
            CuratedChannel.objects.filter(is_active=True).values_list("handle", flat=True)
        )
        if not handles:
            logger.info("YouTubeChannelsCollector: 등록된 큐레이션 채널 없음 — Admin/Channels에서 추가")
            return []

        api_key = settings.YOUTUBE_API_KEY
        results: list[dict] = []
        seen_ids: set[str] = set()

        with httpx.Client(timeout=10.0) as client:
            for handle in handles:
                params = {"part": "snippet,contentDetails", "key": api_key}
                if handle.startswith("UC") and not handle.startswith("@"):
                    params["id"] = handle  # channel ID 직접 조회
                else:
                    params["forHandle"] = handle  # @핸들 조회
                try:
                    ch_resp = client.get(CHANNELS_ENDPOINT, params=params)
                    ch_resp.raise_for_status()
                    items = ch_resp.json().get("items", [])
                    if not items:
                        logger.warning("youtube_channels: %s 채널 없음", handle)
                        continue
                    ch = items[0]
                    uploads_id = (
                        ch.get("contentDetails", {})
                        .get("relatedPlaylists", {})
                        .get("uploads")
                    )
                    ch_title = ch.get("snippet", {}).get("title", handle)
                    if not uploads_id:
                        continue

                    pl_resp = client.get(
                        PLAYLIST_ITEMS_ENDPOINT,
                        params={
                            "part": "snippet,contentDetails",
                            "playlistId": uploads_id,
                            "maxResults": ITEMS_PER_CHANNEL,
                            "key": api_key,
                        },
                    )
                    pl_resp.raise_for_status()
                    for pi in pl_resp.json().get("items", []):
                        snippet = pi.get("snippet", {})
                        vid = (
                            pi.get("contentDetails", {}).get("videoId")
                            or snippet.get("resourceId", {}).get("videoId")
                        )
                        if not vid or vid in seen_ids:
                            continue
                        seen_ids.add(vid)
                        thumbs = snippet.get("thumbnails", {})
                        thumb = (
                            thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}
                        ).get("url")
                        results.append(
                            {
                                "external_id": vid,
                                "title": (snippet.get("title") or "")[:500],
                                "url": f"https://www.youtube.com/watch?v={vid}",
                                "thumbnail_url": thumb,
                                "published_at": _parse_dt(snippet.get("publishedAt")),
                                "raw_content": snippet.get("description") or "",
                                "metadata": {
                                    "channel": ch_title,
                                    "channel_handle": handle,
                                    "_kind": "curated_channel",
                                },
                            }
                        )
                except httpx.HTTPError as exc:
                    logger.warning("youtube_channels %s 실패: %s", handle, exc)
                    continue

        return results
