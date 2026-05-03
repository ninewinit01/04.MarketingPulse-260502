# MarketingPulse

> 매일 아침 마케팅 담당자가 한 페이지에서 핵심 트렌드/이슈/뉴스를 확인할 수 있는 대시보드.
> 자세한 기획은 [`plan.md`](./plan.md), 현재까지 구축 현황은 [`report.md`](./report.md) 참고.

## 구조

```
marketing-pulse/
├── backend/    Django 5 + DRF + MariaDB (Docker)
├── frontend/   React 18 + Vite + TS + Tailwind + shadcn/ui (npm)
├── plan.md     기획서
├── report.md   개발 현황
└── DEPLOY.md   배포 가이드 (3가지 시나리오 상세)
```

| 레이어 | 기술 | 포트 (기본) |
|--------|------|-----------|
| Frontend | React 18 / Vite / TS | 5173 |
| Backend | Django 5 + DRF + gunicorn | 8181 (호스트) → 8000 (컨테이너) |
| DB | MariaDB 11 | 3306 (컨테이너 내부만) |
| Reverse Proxy (prod 옵션) | Caddy 2 | 80, 443 |

```
[브라우저] ─HTTPS─▶ [Caddy(prod) 또는 직접] ─▶ [Django+gunicorn] ─SQL─▶ [MariaDB]
                                                    │
                                                    ├─ Naver News / DataLab API
                                                    ├─ YouTube Data API
                                                    └─ Google News RSS (마케팅)
```

---

## 빠른 시작 (가장 단순한 로컬 dev)

### 사전 준비
- **Docker Desktop** (또는 Docker + Compose v2)
- **Node 20+** + `npm`
- (선택) **외부 API 키** — 비워두면 mock 데이터로 동작

### 1. Backend (Docker)
```bash
cd backend
cp .env.example .env
# 에디터로 .env 열어서 DB_PASSWORD, ADMIN_API_TOKEN 등 채우기 (아래 환경변수 표 참고)
make init
```

### 2. Frontend (npm)
```bash
cd frontend
cp .env.example .env
# .env 안의 VITE_API_BASE_URL=http://localhost:8181/api 확인
npm install
npm run dev
```

### 3. 접속
- 대시보드: http://localhost:5173
- Admin: http://localhost:5173/admin → 좌측 토큰 입력 칸에 `.env`의 `ADMIN_API_TOKEN` 붙여넣기
- API: http://localhost:8181/api/health/

---

## 환경변수 가이드

### Backend (`backend/.env`)

| 변수 | 발급/생성 방법 | 필수? |
|------|----------------|-------|
| `DB_NAME`, `DB_USER` | 자유 (예: `marketing_pulse`, `mp_user`) | ✅ |
| `DB_PASSWORD`, `DB_ROOT_PASSWORD` | `openssl rand -hex 16` | ✅ |
| `DJANGO_SECRET_KEY` | `openssl rand -base64 50` | ✅ |
| `ADMIN_API_TOKEN` | `openssl rand -hex 32` (관리자 인증) | ✅ |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` (dev) / 도메인 또는 IP (배포) | ✅ |
| `CORS_ALLOWED_ORIGINS` | frontend URL (예: `http://localhost:5173`) | ✅ |
| `NAVER_CLIENT_ID` + `NAVER_CLIENT_SECRET` | https://developers.naver.com/apps/ — "검색" + "데이터랩" 둘 다 체크 | 권장 |
| `YOUTUBE_API_KEY` | Google Cloud Console → YouTube Data API v3 활성화 → API 키 | 권장 |
| `NEWSAPI_KEY` | https://newsapi.org/register | 선택 (없으면 Google News RSS 폴백) |
| `LLM_PROVIDER`, `LLM_API_KEY` | (Phase 2 기능, 미구현) | ❌ |
| `TIME_ZONE` | `Asia/Seoul` (기본) | ✅ |

> 외부 API 키 비워둬도 collector가 **mock 데이터**로 동작 — UI/구조 테스트 가능.

### Frontend (`frontend/.env`)

| 변수 | 값 |
|------|---|
| `VITE_API_BASE_URL` | dev: `http://localhost:8181/api` / 외부: `https://api.your-domain.com/api` |

---

## 배포 옵션 요약

자세한 단계는 [`DEPLOY.md`](./DEPLOY.md) 참고.

| 옵션 | 용도 | 핵심 |
|------|------|------|
| **A. 로컬 PC** | 개발 / 시연 / 테스트 | docker compose + npm dev — 위 "빠른 시작" |
| **B. 홈서버 LAN** | 사내/가정 네트워크 사용자 | LAN IP로 ALLOWED_HOSTS / CORS / VITE_API_BASE_URL 변경 |
| **C. 도메인 + HTTPS** | 외부 접근 (정식 운영) | DNS A 레코드 + 라우터 80/443 포트포워딩 + Caddy 자동 인증서 + crontab 등록 |

---

## 자주 쓰는 명령

### Backend (`cd backend`)
```bash
make help            # 전체 명령
make init            # 첫 실행: build + up + migrate + seed + collect
make up / down       # 컨테이너 시작 / 중지
make collect         # 수집 1회 수동 실행
make logs            # 로그 follow
make health          # /api/health/ 호출
make superuser       # Django Admin 계정
make shell           # Django shell
make dbshell         # MariaDB CLI
make nuke            # 컨테이너 + DB 볼륨 전부 제거
make reset           # nuke + init
```

### Production (`cd backend`)
```bash
make prod-up         # gunicorn + caddy + db 빌드/실행
make prod-init       # prod 첫 실행 (migrate + seed + collect 포함)
make prod-collect    # prod 수집
make prod-logs       # prod 로그
```

### Frontend (`cd frontend`)
```bash
npm run dev          # dev 서버
npm run build        # 프로덕션 빌드 → dist/
npm run preview      # 빌드 결과 로컬 프리뷰
```

---

## 주요 기능 / API

- 메인 대시보드 (오늘의 핫이슈 · 네이버 검색 트렌드 TOP10 · 마케팅 영상 TOP · 큐레이션 채널 · 업종별 카드)
- 5개 업종 (법률/병원/의류/숙박/식당) × 90개 키워드 자동 분류
- Admin: 업종/키워드/소스/유튜브 채널/수집 로그 CRUD (Bearer 토큰)
- 매일 KST 08:00 자동 수집 (cron 등록 시)

### Public API
| Method | Path |
|--------|------|
| GET | `/api/health/` |
| GET | `/api/dashboard/?date=YYYY-MM-DD` |
| GET | `/api/industries/` |
| GET | `/api/content/?date=&industry=&source=` |
| GET | `/api/trends/?date=&source=` |

### Admin API (`Authorization: Bearer <ADMIN_API_TOKEN>`)
| Method | Path |
|--------|------|
| CRUD | `/api/admin/industries/` |
| CRUD | `/api/admin/keywords/?industry=<id>` |
| GET/PATCH | `/api/admin/sources/` |
| CRUD | `/api/admin/channels/` (YouTube 큐레이션) |
| GET | `/api/admin/runs/` |
| POST | `/api/admin/runs/trigger/` |

---

## 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-----------|
| `vite: command not found` | `cd frontend && npm install` 안 했음 |
| Frontend에서 backend 호출 시 CORS 에러 | `backend/.env` 의 `CORS_ALLOWED_ORIGINS` 에 frontend URL 추가 후 `docker compose up -d --force-recreate backend` (단순 restart는 env 갱신 안 됨) |
| `No CORS_ALLOW_ORIGIN` 헤더가 응답에 없음 | 위와 동일 — `--force-recreate` 필요 |
| Admin 페이지 401/403 | 토큰 잘못 입력. localStorage 비우고 다시: `localStorage.removeItem("admin_token")` |
| `make init` 시 `mysqlclient` 빌드 실패 | Dockerfile에 `default-libmysqlclient-dev` 들어있음 — `docker compose build --no-cache backend` |
| 포트 충돌 (3306, 8181, 5173) | 호스트에 다른 서비스가 점유 중. `backend/docker-compose.yml` 또는 `frontend/vite.config.ts` 의 포트 변경 |
| YouTube `quotaExceeded` 403 | 일 한도 10,000 초과 (디버깅 시 빨리 소진). PT 자정 (KST 오후 4시) 자동 reset, 또는 새 GCP 프로젝트 키 |
| 자동 수집 안 됨 | crontab 등록 확인: `crontab -l`. 시스템 시간대 KST: `timedatectl set-timezone Asia/Seoul` |
| Vercel SPA 라우팅에서 새로고침 시 404 | `frontend/vercel.json` 의 rewrites 확인 (이미 포함됨) |
| Vite 환경변수 변경 후 안 반영 | Vite는 빌드 타임에 박힘 → `npm run build` 또는 dev 서버 재시작 |

---

## 보안 주의사항

- **`.env` 절대 commit 금지** — `.gitignore`에 `**/.env` 처리됨, 그래도 `git status`로 확인 권장
- **`ADMIN_API_TOKEN` 강한 값 사용** — 외부 노출 시 32+ 글자 (`openssl rand -hex 32`)
- **DB 포트 (3306) 외부 노출 X** — `docker-compose.yml` 에서 `expose` 만, `ports` 매핑 X
- **외부 API 키는 본인 명의** 발급 — 우리 키 X
- **외부 도메인 운영 시 HTTPS 필수** — Caddy 자동 Let's Encrypt
- **첫 배포 후 ADMIN_API_TOKEN 백업** — 분실 시 admin 페이지 사용 불가, DB에서 직접 조회 또는 `.env` 변경 + restart 필요
- **DB 백업** — docker volume `db_data` 정기 백업 권장 (`docker run --rm -v marketingtrends_db_data:/data -v $(pwd):/backup alpine tar czf /backup/db-$(date +%F).tgz /data`)

---

## 외부 API 키 발급 비용

| API | 무료 한도 | 한도 초과 시 |
|-----|----------|----------------|
| 네이버 (검색 + DataLab) | 25,000건/일 + 1,000건/일 | 그냥 차단 (자동 과금 X) |
| YouTube Data API v3 | 10,000 quota/일 | 차단. 카드 등록 + quota 인상 신청해야만 과금 |
| Google News RSS | 무제한 | — |
| NewsAPI (선택) | 100req/일, localhost 전용 | 배포 시 유료 — RSS로 대체 권장 |

운영 중 자동 과금 0원 가능 (카드 등록 안 하면 한도 초과 시 그냥 차단).

---

## Phase 2 로드맵

`plan.md` §13 + `report.md` §5 참고. 핵심:
- **LLM 자동 요약/분류** (Claude/OpenAI API — 추상 인터페이스 이미 있음)
- **이메일/슬랙 매일 푸시 알림**
- **인스타/틱톡/X 데이터 수집** (Apify/Bright Data 등)
- **차트/그래프 시각화**
- **사용자 인증 + 멀티 테넌시**
