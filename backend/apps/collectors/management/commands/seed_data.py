"""5개 업종 + 키워드 + 4개 Source 시드.

기본은 idempotent (이미 있으면 skip).
--replace: 5개 업종의 기존 키워드를 모두 삭제하고 새 리스트로 교체.
"""
from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.content.models import CuratedChannel, Source
from apps.industries.models import Industry, Keyword

INDUSTRIES = [
    {
        "name": "법률",
        "slug": "legal",
        "sort_order": 10,
        "keywords": [
            "변호사", "법률사무소", "로펌", "리걸테크", "법률상담", "법무법인",
            "온라인 법률서비스", "법률 플랫폼", "법률 마케팅", "변호사 광고",
            "로톡", "로앤굿", "법률 AI", "판례검색", "전자소송",
        ],
    },
    {
        "name": "병원",
        "slug": "hospital",
        "sort_order": 20,
        "keywords": [
            "병원 마케팅", "의원 마케팅", "의료광고", "비급여", "피부과", "성형외과",
            "치과", "한의원", "진료비", "환자유치", "의료 SNS", "메디컬 마케팅",
            "실손보험", "비대면진료", "닥터나우", "굿닥", "강남언니", "바비톡",
        ],
    },
    {
        "name": "의류",
        "slug": "fashion",
        "sort_order": 30,
        "keywords": [
            "패션", "의류", "브랜드", "F/W", "S/S", "컬렉션", "무신사", "에이블리", "지그재그",
            "29CM", "패션 트렌드", "스트릿 패션", "Y2K", "코어룩", "OOTD",
            "패션 인플루언서", "룩북", "시즌오프", "콜라보", "캠페인",
        ],
    },
    {
        "name": "숙박",
        "slug": "lodging",
        "sort_order": 40,
        "keywords": [
            "호텔", "펜션", "풀빌라", "게스트하우스", "한옥스테이", "스테이폴리오",
            "야놀자", "여기어때", "에어비앤비", "호캉스", "워케이션", "럭셔리 호텔",
            "호텔 마케팅", "OTA", "객실", "패키지 상품", "시즌 프로모션", "부킹닷컴",
        ],
    },
    {
        "name": "식당",
        "slug": "restaurant",
        "sort_order": 50,
        "keywords": [
            "맛집", "외식", "외식업", "오마카세", "다이닝", "미쉐린", "블루리본",
            "배달의민족", "쿠팡이츠", "요기요", "캐치테이블", "망고플레이트",
            "식당 마케팅", "푸드 트렌드", "핫플", "인스타 맛집", "팝업 레스토랑",
            "스몰브랜드", "비건 레스토랑",
        ],
    },
]

SOURCES = [
    {"slug": "naver_news", "name": "네이버 뉴스", "type": Source.Type.NEWS},
    {"slug": "naver_datalab", "name": "네이버 DataLab", "type": Source.Type.SEARCH_TREND},
    {"slug": "youtube", "name": "YouTube (마케팅 검색)", "type": Source.Type.VIDEO},
    {"slug": "youtube_channels", "name": "YouTube (큐레이션 채널)", "type": Source.Type.VIDEO},
    {"slug": "newsapi", "name": "일반 뉴스 (RSS/NewsAPI)", "type": Source.Type.NEWS},
]

# YouTube 큐레이션 채널 — Admin > YouTube 채널 페이지에서 자유롭게 추가/수정 가능
CURATED_CHANNELS = [
    {
        "handle": "@eo_korea",
        "name": "EO Korea",
        "description": "스타트업/비즈니스 인터뷰",
    },
    {
        "handle": "@CH신사임당",
        "name": "신사임당",
        "description": "비즈니스/유튜브 운영",
    },
]


class Command(BaseCommand):
    help = "초기 업종 / 키워드 / 소스 시드 데이터를 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="기존 키워드를 모두 삭제하고 새 리스트로 교체",
        )

    def handle(self, *args, **opts):
        replace = opts.get("replace", False)

        for ind_data in INDUSTRIES:
            industry, created = Industry.objects.get_or_create(
                slug=ind_data["slug"],
                defaults={
                    "name": ind_data["name"],
                    "sort_order": ind_data["sort_order"],
                },
            )
            label = "생성" if created else "존재"
            self.stdout.write(f"  [{label}] Industry: {industry.name}")

            if replace:
                deleted, _ = industry.keywords.all().delete()
                if deleted:
                    self.stdout.write(self.style.WARNING(f"    - 기존 키워드 {deleted}개 삭제"))

            added = 0
            for term in ind_data["keywords"]:
                _, kw_created = Keyword.objects.get_or_create(industry=industry, term=term)
                if kw_created:
                    added += 1
            self.stdout.write(f"    + 키워드 {added}개 추가 (총 {industry.keywords.count()}개)")

        for src_data in SOURCES:
            source, created = Source.objects.get_or_create(
                slug=src_data["slug"],
                defaults={"name": src_data["name"], "type": src_data["type"]},
            )
            label = "생성" if created else "존재"
            self.stdout.write(f"  [{label}] Source: {source.name}")

        for ch_data in CURATED_CHANNELS:
            ch, created = CuratedChannel.objects.get_or_create(
                handle=ch_data["handle"],
                defaults={
                    "name": ch_data["name"],
                    "description": ch_data["description"],
                    "is_active": True,
                },
            )
            label = "생성" if created else "존재"
            self.stdout.write(f"  [{label}] CuratedChannel: {ch.handle} ({ch.name})")

        self.stdout.write(self.style.SUCCESS("\n시드 데이터 준비 완료"))
        self.stdout.write(f"\nADMIN_API_TOKEN = {settings.ADMIN_API_TOKEN}")
