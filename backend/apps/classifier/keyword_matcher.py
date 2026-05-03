"""키워드 substring 매칭 분류기 (MVP).

Phase 2에서 LLM 분류로 대체 예정. 현재는 단순:
  - 활성 Keyword.term이 텍스트(title + raw_content)에 포함되면 해당 Industry 태깅
  - 다중 매칭 가능 (한 콘텐츠가 여러 업종에 속할 수 있음)
"""
from collections.abc import Iterable

from apps.industries.models import Industry, Keyword


def get_active_keywords() -> list[Keyword]:
    return list(
        Keyword.objects.filter(is_active=True, industry__is_active=True).select_related("industry")
    )


def match_industries(text: str, keywords: Iterable[Keyword] | None = None) -> list[Industry]:
    if not text:
        return []
    if keywords is None:
        keywords = get_active_keywords()

    haystack = text.lower()
    matched_ids: set[int] = set()
    matched: list[Industry] = []
    for kw in keywords:
        if kw.term.lower() in haystack and kw.industry_id not in matched_ids:
            matched_ids.add(kw.industry_id)
            matched.append(kw.industry)
    return matched
