"""각 collector가 API 키 없을 때 반환할 mock 데이터.

업종별 키워드를 어느 정도 포함시켜서 keyword_matcher가 매칭하도록 구성.
demo / 개발 환경 전용.
"""
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def _now():
    return datetime.now(KST)


def naver_news_mock() -> list[dict]:
    now = _now()
    samples = [
        ("법무부, 변호사 광고 규정 개정안 발표", "법률사무소 업계의 광고 자율화 폭이 확대될 전망"),
        ("강남 성형외과 트렌드 — 자연스러운 시술 인기", "병원 마케팅에서 후기 콘텐츠의 영향력 증가"),
        ("의류 브랜드 '러브미' 봄 신상 출시", "의류 업계 신상 매출 호조"),
        ("호텔·숙박 예약 플랫폼 경쟁 심화", "숙박 업계 OTA 의존도 다시 화두"),
        ("미쉐린 가이드 서울 2026 발표 — 신규 식당 12곳 등재", "식당 업계 미슐랭 효과 본격화"),
        ("2026년 마케팅 트렌드: AI 콘텐츠 자동화", "전 업종 공통 트렌드"),
    ]
    return [
        {
            "external_id": f"naver_news_mock_{i}",
            "title": title,
            "url": f"https://news.naver.com/mock/{i}",
            "thumbnail_url": None,
            "published_at": now - timedelta(hours=i),
            "raw_content": desc,
            "metadata": {"mock": True, "publisher": "Mock뉴스"},
        }
        for i, (title, desc) in enumerate(samples, start=1)
    ]


def naver_datalab_mock() -> list[dict]:
    """키워드별 검색량 순위 mock. observed_at은 일자 자정으로 고정."""
    now = _now()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    samples = [
        ("배달의민족", "식당", "restaurant", 95),
        ("무신사", "의류", "fashion", 88),
        ("야놀자", "숙박", "lodging", 82),
        ("쿠팡이츠", "식당", "restaurant", 76),
        ("로톡", "법률", "legal", 71),
        ("강남언니", "병원", "hospital", 65),
        ("에이블리", "의류", "fashion", 60),
        ("호캉스", "숙박", "lodging", 54),
        ("미쉐린", "식당", "restaurant", 48),
        ("성형외과", "병원", "hospital", 42),
    ]
    return [
        {
            "kind": "trend",
            "external_id": f"naver_search_{kw}_{now:%Y%m%d}",
            "title": kw,
            "url": f"https://search.naver.com/search.naver?query={kw}",
            "keyword": kw,
            "rank": rank,
            "observed_at": day_start,
            "metadata": {
                "mock": True,
                "ratio": ratio,
                "industry_name": ind_name,
                "industry_slug": ind_slug,
            },
        }
        for rank, (kw, ind_name, ind_slug, ratio) in enumerate(samples, start=1)
    ]


def youtube_mock() -> list[dict]:
    """A (마케팅 토픽 인기 영상) + B (업종별 영상) mock."""
    now = _now()
    a_samples = [
        ("브랜드 마케팅의 핵심 — 무신사가 4조 매출 만든 이유", "마케팅 인사이트"),
        ("AI 광고 시대 — 2026 트렌드 총정리", "광고 트렌드"),
        ("인플루언서 마케팅 ROI 측정하는 법", "마케팅 강의"),
        ("쿠팡 vs 컬리 — 이커머스 브랜드 전쟁", "이커머스 분석"),
    ]
    b_samples = [
        ("변호사 마케팅, 절대 하면 안 되는 5가지", "법률", "legal"),
        ("강남 성형외과 마케팅 — 후기 콘텐츠 활용법", "병원", "hospital"),
        ("패션 브랜드 SNS 운영 노하우", "의류", "fashion"),
        ("호텔 마케팅 — OTA 의존도 줄이는 법", "숙박", "lodging"),
        ("맛집 마케팅, 인스타로 손님 늘리는 비법", "식당", "restaurant"),
    ]
    items = []
    for i, (title, desc) in enumerate(a_samples, start=1):
        items.append(
            {
                "external_id": f"yt_a_mock_{i}",
                "title": title,
                "url": f"https://www.youtube.com/watch?v=mock_a_{i}",
                "thumbnail_url": f"https://i.ytimg.com/vi/mock_a_{i}/hqdefault.jpg",
                "published_at": now - timedelta(hours=i * 2),
                "raw_content": desc,
                "metadata": {"mock": True, "_kind": "marketing_top", "channel": "Mock 마케팅"},
            }
        )
    for i, (title, ind_name, ind_slug) in enumerate(b_samples, start=1):
        items.append(
            {
                "external_id": f"yt_b_mock_{i}",
                "title": title,
                "url": f"https://www.youtube.com/watch?v=mock_b_{i}",
                "thumbnail_url": f"https://i.ytimg.com/vi/mock_b_{i}/hqdefault.jpg",
                "published_at": now - timedelta(hours=i),
                "raw_content": "",
                "metadata": {
                    "mock": True,
                    "_kind": "industry",
                    "industry_slug": ind_slug,
                    "industry_name": ind_name,
                    "channel": f"Mock {ind_name} 채널",
                },
            }
        )
    return items


def youtube_channels_mock() -> list[dict]:
    """큐레이션 채널 영상 mock."""
    now = _now()
    samples = [
        ("EO", "스타트업이 살아남는 마케팅 전략 5가지"),
        ("EO", "[다큐] 신생 브랜드가 1년 만에 100억 매출 만든 비결"),
        ("김미경TV", "당신의 브랜드가 안 팔리는 진짜 이유"),
        ("체인지그라운드", "콘텐츠 마케팅, 이렇게만 하면 됩니다"),
        ("자청유튜브대학", "광고 없이 매출 10배 만든 브랜드 분석"),
        ("퍼블리", "2026 마케터가 꼭 알아야 할 트렌드"),
    ]
    return [
        {
            "external_id": f"yt_ch_mock_{i}",
            "title": title,
            "url": f"https://www.youtube.com/watch?v=mock_ch_{i}",
            "thumbnail_url": f"https://i.ytimg.com/vi/mock_ch_{i}/hqdefault.jpg",
            "published_at": now - timedelta(hours=i * 4),
            "raw_content": "",
            "metadata": {
                "mock": True,
                "channel": ch,
                "channel_handle": f"@{ch.lower()}",
                "_kind": "curated_channel",
            },
        }
        for i, (ch, title) in enumerate(samples, start=1)
    ]


def news_rss_mock() -> list[dict]:
    now = _now()
    samples = [
        "오늘의 헤드라인: 국내 경제 지표 발표",
        "글로벌 마케팅 트렌드 보고서 공개",
        "K-콘텐츠 수출 사상 최고치 기록",
        "AI 광고 시장 50% 성장 전망",
        "소비자 트렌드 — Z세대의 의류 소비 변화",
    ]
    return [
        {
            "external_id": f"rss_mock_{i}",
            "title": title,
            "url": f"https://news.example.com/article/{i}",
            "thumbnail_url": None,
            "published_at": now - timedelta(hours=i),
            "raw_content": title,
            "metadata": {"mock": True, "source_name": "MockNews"},
        }
        for i, title in enumerate(samples, start=1)
    ]
