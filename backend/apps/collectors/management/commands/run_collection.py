"""매일 08:00 KST 실행되는 메인 수집 명령.

usage:
  python manage.py run_collection
  python manage.py run_collection --source naver_news
  python manage.py run_collection --date 2026-04-27
"""
from __future__ import annotations

import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.classifier.keyword_matcher import get_active_keywords, match_industries
from apps.collectors.registry import get_collector_class
from apps.content.models import CollectionRun, ContentItem, Source, TrendKeyword

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "활성 Source 전체에 대해 1회 수집을 실행."

    def add_arguments(self, parser):
        parser.add_argument("--source", type=str, default=None, help="특정 source.slug만 실행")
        parser.add_argument("--date", type=str, default=None, help="기준 날짜 YYYY-MM-DD")

    def handle(self, *args, **opts):
        run_date = (
            datetime.strptime(opts["date"], "%Y-%m-%d").date()
            if opts.get("date")
            else timezone.localdate()
        )

        sources = Source.objects.filter(is_active=True)
        if opts.get("source"):
            sources = sources.filter(slug=opts["source"])

        if not sources.exists():
            self.stdout.write(self.style.WARNING("실행할 활성 Source 없음"))
            return

        keywords = get_active_keywords()
        total = 0
        for source in sources:
            cls = get_collector_class(source.slug)
            if cls is None:
                self.stdout.write(self.style.WARNING(f"  - {source.slug}: collector 미등록, skip"))
                continue

            run = CollectionRun.objects.create(source=source, status=CollectionRun.Status.RUNNING)
            self.stdout.write(f"▶ {source.slug} 수집 시작")
            try:
                items = cls(source).collect(run_date)
                saved = self._persist(source, items, keywords)
                run.items_collected = saved
                run.status = CollectionRun.Status.SUCCESS
                total += saved
                self.stdout.write(self.style.SUCCESS(f"  ✓ {source.slug}: {saved}건 저장"))
            except Exception as exc:  # noqa: BLE001
                logger.exception("collector %s 실패", source.slug)
                run.status = CollectionRun.Status.FAILED
                run.error_message = str(exc)[:1000]
                self.stdout.write(self.style.ERROR(f"  ✗ {source.slug}: {exc}"))
            finally:
                run.finished_at = timezone.now()
                run.save()

        self.stdout.write(self.style.SUCCESS(f"\n총 {total}건 수집 완료"))

    @transaction.atomic
    def _persist(self, source: Source, items: list[dict], keywords) -> int:
        saved = 0
        for item in items:
            kind = item.get("kind", "content")
            if kind == "trend":
                self._save_trend(source, item)
            else:
                self._save_content(source, item, keywords)
            saved += 1
        return saved

    def _save_content(self, source: Source, data: dict, keywords) -> None:
        defaults = {
            "title": data["title"],
            "url": data["url"],
            "thumbnail_url": data.get("thumbnail_url"),
            "published_at": data.get("published_at"),
            "raw_content": data.get("raw_content", ""),
            "metadata": data.get("metadata", {}),
        }
        item, _ = ContentItem.objects.update_or_create(
            source=source,
            external_id=data["external_id"][:255],
            defaults=defaults,
        )
        text = f"{data['title']} {data.get('raw_content', '')}"
        industries = match_industries(text, keywords)
        if industries:
            item.industries.set(industries)

    def _save_trend(self, source: Source, data: dict) -> None:
        from apps.industries.models import Industry

        tk, _ = TrendKeyword.objects.update_or_create(
            source=source,
            keyword=data["keyword"],
            observed_at=data.get("observed_at") or timezone.now(),
            defaults={
                "rank": data.get("rank", 0),
                "metadata": data.get("metadata", {}),
            },
        )
        ind_slug = (data.get("metadata") or {}).get("industry_slug")
        if ind_slug:
            try:
                ind = Industry.objects.get(slug=ind_slug)
                tk.industries.set([ind])
            except Industry.DoesNotExist:
                pass
