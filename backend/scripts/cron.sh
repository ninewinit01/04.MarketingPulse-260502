#!/usr/bin/env bash
# 매일 KST 08:00 호스트 cron이 실행. VM의 timezone은 Asia/Seoul.
set -euo pipefail

cd /opt/marketing-trends/backend

LOG=/var/log/mp-collect.log

echo "" >> "$LOG"
echo "=== $(date -Iseconds) run_collection 시작 ===" >> "$LOG"
docker compose -f docker-compose.prod.yml exec -T backend \
    python manage.py run_collection >> "$LOG" 2>&1 || {
    echo "!!! run_collection 실패 (exit=$?)" >> "$LOG"
    exit 1
}
echo "=== $(date -Iseconds) run_collection 종료 ===" >> "$LOG"
