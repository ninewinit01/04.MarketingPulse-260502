# 배포 후 운영 가이드

`make init` 으로 빌드/마이그레이션/시드/첫 수집까지 끝났다고 가정. 이후 운영 흐름을 단계별로.

---

## 1. 시드 데이터 확인 (자동으로 들어감)

`make init` 또는 `make seed` 가 자동으로 다음을 만듭니다 — 별도 admin 입력 불필요:

| 항목 | 개수 | 비고 |
|------|------|------|
| **Industry (업종)** | 5 | 법률 / 병원 / 의류 / 숙박 / 식당 |
| **Keyword** | 90 | 업종별 15-20개 (변호사, 로톡, 무신사, 야놀자, 배달의민족 등) |
| **Source** | 5 | naver_news / naver_datalab / youtube / youtube_channels / newsapi |
| **CuratedChannel** | 2 | `@eo_korea` (EO Korea), `@CH신사임당` (신사임당) |

> 모두 `backend/apps/collectors/management/commands/seed_data.py` 에 코드화되어 있습니다. 운영 환경 (실서버) 셋업과 100% 동일한 초기 상태.

---

## 2. Admin 페이지 진입

1. 브라우저에서 `http://localhost:5173/admin` (또는 본인 호스트)
2. 좌측 사이드바 하단 **Admin Token** 칸에 `backend/.env` 의 `ADMIN_API_TOKEN` 값 붙여넣기 → **저장**
3. 페이지 자동 reload, 토큰은 localStorage에 저장됨

| 메뉴 | 기능 |
|------|------|
| **Industries** | 업종 추가/수정/삭제 (slug 변경, sort_order, 활성 토글) |
| **Keywords** | 업종별 카드 그리드 — 칩으로 키워드 추가/삭제, 가중치 클릭 시 수정, 칩 클릭 시 활성/비활성 토글 |
| **Sources** | 5개 데이터 소스 활성/비활성 토글 |
| **YouTube 채널** | `@핸들` 또는 `UCxxxxx` channel ID로 큐레이션 채널 등록 |
| **Runs** | 최근 50개 수집 로그 + "수동 수집 실행" 버튼 |

---

## 3. 첫 수집 실행 (mock 또는 실제 API)

```bash
cd backend
make collect
```

- **외부 API 키 채워둔 경우**: 실제 데이터 ~250-500건 수집 (네이버 뉴스 ~200, DataLab 30, YouTube 40, RSS 20)
- **키 비워둔 경우**: 각 collector가 mock 데이터로 30건 정도

확인:
- 대시보드 새로고침 → "🏷️ 업종별" 카드 5개에 콘텐츠
- Admin > Runs → 마지막 수집 결과 (성공/실패/건수)

---

## 4. 자동 수집 등록 (매일 KST 오전 8시)

```bash
# 시스템 시간대를 KST로 (호스트 시간이 KST 아니면)
sudo timedatectl set-timezone Asia/Seoul

# cron.sh 실행 권한
chmod +x backend/scripts/cron.sh

# crontab 등록 — 매일 KST 08:00
( crontab -l 2>/dev/null; echo "0 8 * * * $(pwd)/backend/scripts/cron.sh" ) | crontab -

# 확인
crontab -l
```

- 로그: `backend/logs/collect.log` (스크립트가 자동 생성)
- 수동 테스트: `backend/scripts/cron.sh && tail backend/logs/collect.log`

> 다음날 오전 8시 이후 `tail -f backend/logs/collect.log` 로 실행 확인 가능. 첫 cron 실행 전이면 위 수동 테스트로 파이프라인 검증.

---

## 5. 운영 중 데이터 변경

### 5.1 새 업종 추가 (예: "반려동물")
1. Admin > Industries → **+ 추가**
2. 이름: `반려동물`, slug: `pet`, 정렬 순서: `60`, 활성 ☑ → **저장**
3. Admin > Keywords → "반려동물" 카드의 **+** 버튼 → 칩 입력 ("강아지 사료", "동물병원 마케팅" ...)
4. **Admin > Runs > 수동 수집 실행** → 새 키워드로 매칭된 콘텐츠가 그 업종에 자동 분류

### 5.2 키워드 추가/삭제
- Admin > Keywords 카드에서 **+** 로 추가, 칩 우측 ✕ 로 삭제
- 가중치 박스 (`×1`) 클릭 → prompt로 수정 (현재 사용 안 함, Phase 2)
- 칩 본문 클릭 → 활성/비활성 토글 (비활성은 회색 + 취소선 — 다음 수집부터 무시)

### 5.3 YouTube 채널 추가
1. youtube.com에서 추가하고 싶은 채널 페이지 진입 → 주소창에서 `@핸들` 또는 `UCxxxxx` 채널 ID 복사
2. Admin > YouTube 채널 → **+ 추가** → 핸들/ID 입력
3. 다음 `make collect` (또는 cron)부터 그 채널 최신 영상 3건 자동 수집

### 5.4 데이터 소스 끄기
- Admin > Sources → 활성 토글 OFF → 다음 수집에서 그 source skip

---

## 6. 운영 명령

```bash
cd backend

# 상태
make ps                # 컨테이너 상태
make health            # /api/health/

# 로그
make logs              # 전체
make logs-backend      # backend
make logs-db           # mariadb

# 수집
make collect           # 1회 수동
make prod-collect      # prod 환경에서 (docker-compose.prod.yml)

# DB
make dbshell           # MariaDB CLI
make shell             # Django shell

# Django Admin (Bearer 토큰 외 별도 staff 계정 필요할 때)
make superuser         # 계정 생성 → http://host:8181/django-admin/

# 정리
make down              # 중지 (volume 유지)
make nuke              # 컨테이너 + volume 전부 제거 (DB 초기화 — 위험)
make reset             # nuke + init
```

---

## 7. 데이터 백업 / 복원

### 백업
```bash
# Docker volume 이름 확인 (compose 프로젝트명에 따라 다름 — 보통 marketingtrends_db_data 또는 marketing-trends-prod_db_data)
docker volume ls | grep db_data

VOL=marketing-trends-prod_db_data   # 또는 marketingtrends_db_data
docker run --rm -v $VOL:/data -v $(pwd):/backup alpine \
    tar czf /backup/mp-db-$(date +%F).tgz /data
```

### 복원
```bash
docker compose -f docker-compose.prod.yml down
docker volume rm $VOL
docker volume create $VOL
docker run --rm -v $VOL:/data -v $(pwd):/backup alpine \
    tar xzf /backup/mp-db-2026-04-28.tgz -C /
docker compose -f docker-compose.prod.yml up -d
```

> 정기 백업은 cron으로 별도 등록 권장 (예: 매일 새벽 3시).

---

## 8. 트러블슈팅 (운영 중 자주 나오는 케이스)

| 증상 | 원인 / 해결 |
|------|------------|
| `make collect` 시 네이버 429 | 동시 호출 한계. 일부 키워드 fail은 정상, 다음 수집에서 재시도 |
| YouTube `quotaExceeded` 403 | 일 한도 10K 초과 (디버깅 중 빠르게 소진). PT 자정 (KST 오후 4시) 자동 reset, 또는 새 GCP 프로젝트 키 발급 |
| Admin 페이지 401/403 | 토큰 잘못 입력. 브라우저 콘솔에서 `localStorage.removeItem("admin_token")` 후 재입력 |
| `.env` 변경 후 backend가 새 값 안 읽음 | `restart`는 env 갱신 안 함 → `docker compose up -d --force-recreate backend` |
| Frontend가 backend 호출 시 CORS 차단 | `backend/.env` 의 `CORS_ALLOWED_ORIGINS` 에 frontend URL 추가 (https://, 끝 슬래시 없이) → backend recreate |
| 새 키워드 추가했는데 수집해도 매칭 안 됨 | 1) 키워드 활성 상태 확인 2) `make collect` 다시 실행 3) Admin > Runs에서 실패 여부 확인 |
| 큐레이션 채널 등록했는데 영상 안 옴 | 핸들이 정확한지 확인 (youtube.com/@정확한핸들). `make logs-backend` 에서 `youtube_channels: 채널 없음` 로그 확인 |
| Caddy 인증서 발급 실패 | DNS 가 서버 공인 IP를 가리키는지 (`dig api.your-domain.com`) + 라우터 80/443 포트포워딩 확인 |
| docker compose 명령에서 "permission denied" | `sudo usermod -aG docker $USER` 후 재로그인, 또는 명령 앞에 `sudo` |

---

## 9. 자주 쓰는 검증 명령

```bash
# 1. backend 동작
curl http://localhost:8181/api/health/

# 2. 5 업종 시드 확인
curl http://localhost:8181/api/industries/ | python3 -m json.tool

# 3. admin 토큰 동작 (.env의 ADMIN_API_TOKEN 사용)
TOKEN=$(grep ^ADMIN_API_TOKEN backend/.env | cut -d= -f2)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8181/api/admin/industries/ | python3 -m json.tool

# 4. 큐레이션 채널 확인
curl -H "Authorization: Bearer $TOKEN" http://localhost:8181/api/admin/channels/ | python3 -m json.tool

# 5. 최근 수집 로그
curl -H "Authorization: Bearer $TOKEN" http://localhost:8181/api/admin/runs/ | python3 -m json.tool | head -40
```

---

## 10. 이후 코드 업데이트

```bash
cd /path/to/marketing-pulse
git pull

# 모델 변경 없으면
cd backend && docker compose -f docker-compose.prod.yml up -d --build backend

# 모델 변경 있으면 (마이그레이션 필요)
cd backend
docker compose -f docker-compose.prod.yml up -d --build backend
docker compose -f docker-compose.prod.yml exec backend python manage.py makemigrations
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

> 시드 추가 변경 (새 업종/키워드/채널) 있으면 `make prod-seed` 또는 `make prod-init` 으로 재시드 (idempotent — 이미 있는 건 skip).
