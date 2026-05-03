#!/usr/bin/env bash
# 매일 KST 08:00 자동 수집 스크립트.
#
# 등록 방법:
#   sudo timedatectl set-timezone Asia/Seoul   # 시스템 시간대를 KST로
#   ( crontab -l 2>/dev/null; echo "0 8 * * * $(pwd)/scripts/cron.sh" ) | crontab -
#
# 수동 실행:
#   ./scripts/cron.sh
#
# 로그: $LOG_FILE (기본 ./logs/collect.log, 디렉터리 자동 생성)
set -euo pipefail

# 스크립트 위치 기준 backend 디렉터리로 이동 (절대경로 박지 않음)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$BACKEND_DIR"

# docker-compose 파일 자동 감지 (prod 우선, 없으면 dev)
if [ -f docker-compose.prod.yml ]; then
    COMPOSE="docker compose -f docker-compose.prod.yml"
else
    COMPOSE="docker compose"
fi

# 로그 파일
LOG_DIR="${LOG_DIR:-$BACKEND_DIR/logs}"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_FILE:-$LOG_DIR/collect.log}"

echo "" >> "$LOG_FILE"
echo "=== $(date -Iseconds) run_collection 시작 ===" >> "$LOG_FILE"
$COMPOSE exec -T backend python manage.py run_collection >> "$LOG_FILE" 2>&1 || {
    echo "!!! run_collection 실패 (exit=$?)" >> "$LOG_FILE"
    exit 1
}
echo "=== $(date -Iseconds) run_collection 종료 ===" >> "$LOG_FILE"
