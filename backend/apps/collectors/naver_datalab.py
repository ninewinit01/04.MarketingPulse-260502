"""네이버 DataLab 검색량 추이 — 키워드 단위 순위.

활성 키워드를 모두 단독 그룹으로 5개씩 묶어 호출 → 7일 평균 ratio로 정렬 → 상위 30개를
TrendKeyword(rank=1..30)로 저장.

DataLab의 ratio는 "한 호출 안에서 max=100" 으로 정규화된 값이라 호출 간 비교는 부정확.
MVP에서는 호출 내 평균 ratio로 단순 비교 (정확한 비교는 Phase 2에서 anchor 키워드 도입).
"""
from __future__ import annotations

import logging
import time
from datetime import date, datetime, timedelta, timezone

import httpx
from django.conf import settings

from apps.industries.models import Keyword

from .base import BaseCollector
from .mocks import naver_datalab_mock

logger = logging.getLogger(__name__)
ENDPOINT = "https://openapi.naver.com/v1/datalab/search"
KST = timezone(timedelta(hours=9))

CHUNK_SIZE = 5  # DataLab 한 호출당 최대 그룹 수
TOP_N = 30      # 응답 상위 N개만 TrendKeyword로 저장
THROTTLE_SEC = 0.15  # rate limit 회피용 호출 간 sleep


class NaverDataLabCollector(BaseCollector):
    source_slug = "naver_datalab"

    @property
    def use_mock(self) -> bool:
        return not (settings.NAVER_CLIENT_ID and settings.NAVER_CLIENT_SECRET)

    def collect(self, run_date: date) -> list[dict]:
        if self.use_mock:
            logger.info("NaverDataLabCollector: NAVER 키 없음 → mock 사용")
            return naver_datalab_mock()

        end = run_date
        start = end - timedelta(days=7)
        day_start = datetime.combine(end, datetime.min.time()).replace(tzinfo=KST)

        # 활성 키워드 + 매칭 업종 정보
        keywords = list(
            Keyword.objects.filter(is_active=True, industry__is_active=True)
            .select_related("industry")
            .values("term", "industry__name", "industry__slug")
        )
        if not keywords:
            return []

        headers = {
            "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
            "Content-Type": "application/json",
        }

        # 키워드를 5개씩 chunk → 각 키워드 = 단독 그룹으로 호출
        scores: list[dict] = []
        for chunk_start in range(0, len(keywords), CHUNK_SIZE):
            chunk = keywords[chunk_start : chunk_start + CHUNK_SIZE]
            groups = [{"groupName": kw["term"], "keywords": [kw["term"]]} for kw in chunk]
            payload = {
                "startDate": start.strftime("%Y-%m-%d"),
                "endDate": end.strftime("%Y-%m-%d"),
                "timeUnit": "date",
                "keywordGroups": groups,
            }
            try:
                resp = httpx.post(ENDPOINT, headers=headers, json=payload, timeout=10.0)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.warning("datalab chunk 실패 (terms=%s): %s",
                               [k["term"] for k in chunk], exc)
                continue

            for group, kw in zip(resp.json().get("results", []), chunk, strict=False):
                points = group.get("data", [])
                if not points:
                    continue
                avg_ratio = sum(p.get("ratio", 0) for p in points) / len(points)
                scores.append(
                    {
                        "keyword": kw["term"],
                        "industry_name": kw["industry__name"],
                        "industry_slug": kw["industry__slug"],
                        "avg_ratio": avg_ratio,
                    }
                )

            time.sleep(THROTTLE_SEC)

        # 평균 ratio 내림차순 정렬, 상위 N개
        scores.sort(key=lambda s: s["avg_ratio"], reverse=True)
        top = scores[:TOP_N]

        return [
            {
                "kind": "trend",
                "external_id": f"datalab_{s['keyword']}_{end:%Y%m%d}",
                "title": s["keyword"],
                "url": f"https://search.naver.com/search.naver?query={s['keyword']}",
                "keyword": s["keyword"],
                "rank": rank,
                "observed_at": day_start,
                "metadata": {
                    "ratio": round(s["avg_ratio"], 2),
                    "industry_name": s["industry_name"],
                    "industry_slug": s["industry_slug"],
                },
            }
            for rank, s in enumerate(top, start=1)
        ]
