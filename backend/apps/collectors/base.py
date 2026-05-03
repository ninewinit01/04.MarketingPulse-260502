"""Collector 인터페이스.

각 collector는 외부 소스에서 콘텐츠를 가져와 dict 리스트로 반환.
필수 키: external_id, title, url
선택 키: thumbnail_url, published_at(datetime), raw_content, metadata, kind
  - kind: "content" (default) | "trend"
    "trend"면 ContentItem이 아닌 TrendKeyword로 저장됨.
    "trend" 항목은 추가로 keyword(=title), rank, observed_at(datetime) 필요.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    source_slug: str = ""

    def __init__(self, source):
        self.source = source

    @abstractmethod
    def collect(self, run_date: date) -> list[dict]:
        """수집 결과를 dict 리스트로 반환."""

    def health_check(self) -> bool:
        return True

    @property
    def use_mock(self) -> bool:
        """API 키가 없으면 True (mocks.py의 데이터를 반환하도록)."""
        return False
