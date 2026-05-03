"""대시보드 집계 API.

GET /api/dashboard/?date=YYYY-MM-DD&industry=<slug>
→ 한 번 호출로 메인 페이지 전부 그릴 수 있는 JSON.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from functools import reduce
from operator import or_

from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.content.models import ContentItem, TrendKeyword
from apps.content.serializers import ContentItemSerializer, TrendKeywordSerializer
from apps.industries.models import Industry
from apps.industries.serializers import IndustrySerializer

# 핫이슈 안전망 — newsapi 소스가 잘못된 일반 뉴스를 줄 때 대비한 title-only 필터.
# 실제 수집은 news_rss.py에서 마케팅 토픽 RSS 검색으로 좁혀져 있음.
MARKETING_KEYWORDS = [
    "마케팅", "광고", "브랜드", "캠페인", "인플루언서", "콜라보", "컬래버",
    "프로모션", "리브랜딩", "런칭", "팝업스토어",
    "이커머스", "라이브커머스", "쇼핑몰", "MZ세대", "Z세대",
]


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@api_view(["GET"])
@permission_classes([AllowAny])
def dashboard(request):
    target_date = _parse_date(request.query_params.get("date")) or timezone.localdate()
    industry_slug = request.query_params.get("industry")

    start = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
    end = start + timedelta(days=1)

    items_qs = (
        ContentItem.objects.select_related("source")
        .prefetch_related("industries")
        .filter(collected_at__gte=start, collected_at__lt=end)
    )
    if industry_slug:
        items_qs = items_qs.filter(industries__slug=industry_slug).distinct()

    # 오늘의 핫이슈 — newsapi 중 마케팅 키워드 매칭. 최근 3일 윈도우 (당일 매칭 부족 대비).
    hot_window_start = end - timedelta(days=3)
    news_qs = (
        ContentItem.objects.select_related("source")
        .prefetch_related("industries")
        .filter(source__slug="newsapi", collected_at__gte=hot_window_start)
    )
    keyword_q = reduce(
        or_,
        (Q(title__icontains=kw) for kw in MARKETING_KEYWORDS),
    )
    news_filtered = news_qs.filter(keyword_q)
    news = (news_filtered if news_filtered.exists() else news_qs)[:10]

    # 업종별 그룹핑 — 각 업종별로 별도 쿼리 (다른 source가 limit을 잡아먹지 않게)
    # newsapi(일반 뉴스) 제외. youtube industry 영상은 metadata.industry_slug 직접 매칭.
    base_qs = items_qs.exclude(source__slug="newsapi")
    industries_for_grouping = Industry.objects.filter(is_active=True)
    by_industry: dict[str, list] = {}
    for ind in industries_for_grouping:
        ind_qs = base_qs.filter(
            Q(industries=ind) | Q(metadata__industry_slug=ind.slug)
        ).distinct()[:8]
        by_industry[ind.slug] = list(ind_qs)

    # 트렌드: 네이버 검색 + YouTube — 같은 (source, rank)가 여러 번 수집됐으면 최신 1건만
    trend_qs = (
        TrendKeyword.objects.select_related("source")
        .filter(observed_at__gte=start, observed_at__lt=end)
        .order_by("source__slug", "rank", "-observed_at")
    )
    seen_ranks: set[tuple[str, int]] = set()
    trends_by_source: dict[str, list] = defaultdict(list)
    for tk in trend_qs:
        key = (tk.source.slug, tk.rank)
        if key in seen_ranks:
            continue
        seen_ranks.add(key)
        trends_by_source[tk.source.slug].append(tk)

    # YouTube — A: 마케팅 토픽 인기 영상, C: 큐레이션 채널 영상
    yt_marketing = (
        ContentItem.objects.select_related("source")
        .filter(source__slug="youtube", collected_at__gte=hot_window_start)
        .order_by("-published_at", "-collected_at")[:10]
    )
    # A 응답에는 metadata._kind == "marketing_top" 만 (industry 영상은 업종 카드로 보냄)
    yt_marketing = [i for i in yt_marketing if (i.metadata or {}).get("_kind") != "industry"][:10]

    yt_curated = (
        ContentItem.objects.select_related("source")
        .filter(source__slug="youtube_channels", collected_at__gte=hot_window_start)
        .order_by("-published_at", "-collected_at")[:10]
    )

    industries = Industry.objects.filter(is_active=True)

    return Response(
        {
            "date": target_date.isoformat(),
            "industry": industry_slug,
            "news": ContentItemSerializer(news, many=True).data,
            "by_industry": {
                slug: ContentItemSerializer(items_, many=True).data
                for slug, items_ in by_industry.items()
            },
            "trends": {
                slug: TrendKeywordSerializer(tks, many=True).data
                for slug, tks in trends_by_source.items()
            },
            "youtube_marketing": ContentItemSerializer(list(yt_marketing), many=True).data,
            "youtube_curated": ContentItemSerializer(list(yt_curated), many=True).data,
            "industries": IndustrySerializer(industries, many=True).data,
            "totals": {
                "items": items_qs.distinct().count(),
                "trends": trend_qs.count(),
            },
        }
    )
