# 마케팅 트렌드/이슈 수집 서비스 MVP 기획서

> **프로젝트 코드명**: MarketingPulse (가칭)
> **작성일**: 2026-04-27
> **버전**: v0.2 (MVP)
> **개발 도구**: Claude Code
> **변경점 (v0.1 → v0.2)**: 프론트엔드를 React로 분리, DB를 MariaDB로 변경, 로컬 개발 환경을 Docker Compose로 구성, Admin도 React 기반으로 자체 구현

---

## 1. 프로젝트 개요

### 1.1 목적
매일 아침 마케팅 담당자가 하루 업무를 시작하기 전, **최신 마케팅 트렌드/이슈/뉴스/업종별 사례**를 한 페이지에서 확인할 수 있는 대시보드 서비스.

### 1.2 타깃 사용자
- 1차: 사내 마케팅 팀 (내부 도구)
- 2차 (향후): 외부 고객 대상 SaaS로 확장 가능성 열어둠

### 1.3 핵심 가치 제안
- **시간 절약**: 여러 플랫폼/매체를 일일이 확인할 필요 없이 한 곳에서 확인
- **업종 맞춤**: 자기 사업에 해당하는 업종만 필터링해서 보기
- **시계열 비교**: 날짜별로 누적되어 트렌드 변화 추적 가능

### 1.4 MVP의 범위
> **원칙**: "이번 주 토요일까지 데모 가능한 최소 단위"로 좁힘. 부족한 부분은 Phase 2에서 보강.

---

## 2. MVP 범위 (Scope)

### 2.1 ✅ MVP에 포함
- **데이터 소스 4종**
  - 네이버 DataLab (검색어 트렌드)
  - 네이버 뉴스 검색 API
  - YouTube Data API v3 (인기 동영상 / 키워드 검색)
  - 일반 뉴스 RSS / NewsAPI
- **업종 5종** (초기): 법률, 병원, 의류, 숙박, 식당
- **수집 자동화**: 매일 오전 8시 KST 자동 수집
- **React 기반 대시보드 (SPA)**
  - 오늘의 요약 페이지
  - 날짜별 아카이브
  - 업종별 필터링
- **React 기반 Admin 페이지** (자체 구현)
  - 업종 CRUD
  - 키워드 CRUD
  - 소스 관리
  - 수집 실행 로그 조회 / 수동 트리거
- **LLM 연동 인터페이스 (skeleton만)**
  - 요약/분류 기능은 추후 활성화. 추상화 레이어만 만들어둠.
- **Docker Compose 기반 로컬 개발 환경**

### 2.2 ❌ MVP에서 제외 (Phase 2 이후)
- 인스타그램 / 틱톡 / X(트위터) 트렌드 수집
- LLM 자동 요약 / 자동 분류 (실제 호출)
- 사용자 인증 / 권한 관리 (MVP에서는 단일 어드민 토큰 또는 Basic Auth)
- 이메일/슬랙 푸시 알림
- 차트/그래프 시각화 (텍스트 리스트 위주)
- 모바일 전용 UI (반응형 기본만 적용)

---

## 3. 시스템 아키텍처

### 3.1 기술 스택

| 레이어 | 기술 | 비고 |
|--------|------|------|
| Backend | **Django 5.x + Django REST Framework** | API 전용. 템플릿 미사용 |
| Database | **MariaDB 11.x** | 컨테이너로 실행 |
| Frontend | **React 18 + Vite + TypeScript** | SPA |
| UI 라이브러리 | **Tailwind CSS + shadcn/ui** | Admin CRUD UI를 빠르게 찍어내기 위함 |
| 라우팅 | React Router DOM v6 | |
| 데이터 페칭 | **TanStack Query** (React Query) | 캐싱/리페칭 자동화 |
| API 클라이언트 | axios 또는 fetch | |
| 로컬 환경 | **Docker Compose** | backend / frontend / db 3 서비스 |
| 스케줄러 | 외부 cron (운영) / Docker 내 cron 컨테이너 (로컬 검증) | `python manage.py run_collection` 호출 |
| HTTP 클라이언트 (서버) | `httpx` | 외부 API 호출 |
| 패키지 관리 | `uv` (Python) / `pnpm` (Node) | |

### 3.2 시스템 구성도 (텍스트)

```
[Docker Compose Network]

  ┌──────────────────┐         ┌──────────────────┐
  │  frontend        │  HTTP   │  backend         │
  │  React + Vite    │ ──────▶ │  Django + DRF    │
  │  :5173           │   /api  │  :8000           │
  └──────────────────┘         └────────┬─────────┘
                                         │
                                         │ SQL
                                         ▼
                                ┌──────────────────┐
                                │  db              │
                                │  MariaDB 11      │
                                │  :3306           │
                                └──────────────────┘
                                         ▲
                                         │
              [매일 08:00 KST cron] ─────┘
              python manage.py run_collection
                          │
                          ▼
           ┌───────── Collectors ──────────┐
           │ Naver News / DataLab          │
           │ YouTube Data API              │
           │ NewsAPI / RSS                 │
           └───────────────────────────────┘
```

### 3.3 모노레포 디렉터리 구조

```
marketing_pulse/
├── docker-compose.yml
├── docker-compose.override.yml      # 로컬 개발용 (volume 마운트, hot reload)
├── .env.example
├── README.md
├── PLAN.md                          # 이 기획서
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── manage.py
│   ├── config/                      # Django 프로젝트 설정
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       ├── core/                    # 공통 모델, 유틸
│       ├── industries/              # 업종 + 키워드 (모델 + DRF ViewSet)
│       ├── collectors/              # 데이터 수집 모듈
│       │   ├── base.py
│       │   ├── naver_news.py
│       │   ├── naver_datalab.py
│       │   ├── youtube.py
│       │   ├── news_rss.py
│       │   └── management/commands/run_collection.py
│       ├── content/                 # ContentItem, TrendKeyword (모델 + ViewSet)
│       ├── classifier/              # 키워드 매핑 분류기
│       ├── llm/                     # LLM 추상화 레이어 (스텁)
│       │   ├── base.py
│       │   └── providers/
│       └── dashboard/               # 대시보드 집계 API
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.js
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── lib/
        │   ├── api.ts               # axios 인스턴스
        │   └── queries.ts           # TanStack Query 훅
        ├── components/
        │   └── ui/                  # shadcn/ui 컴포넌트
        ├── pages/
        │   ├── Dashboard.tsx        # 메인 대시보드
        │   ├── Archive.tsx          # 날짜별 아카이브
        │   ├── IndustryDetail.tsx   # 업종별 상세
        │   └── admin/
        │       ├── IndustriesPage.tsx
        │       ├── KeywordsPage.tsx
        │       ├── SourcesPage.tsx
        │       └── CollectionRunsPage.tsx
        └── types/
            └── api.ts               # 백엔드와 공유하는 타입 정의
```

---

## 4. Docker Compose 구성

### 4.1 `docker-compose.yml`

```yaml
services:
  db:
    image: mariadb:11
    restart: unless-stopped
    environment:
      MARIADB_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MARIADB_DATABASE: ${DB_NAME}
      MARIADB_USER: ${DB_USER}
      MARIADB_PASSWORD: ${DB_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    depends_on:
      db:
        condition: service_healthy
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.dev
      DATABASE_URL: mysql://${DB_USER}:${DB_PASSWORD}@db:3306/${DB_NAME}
      NAVER_CLIENT_ID: ${NAVER_CLIENT_ID}
      NAVER_CLIENT_SECRET: ${NAVER_CLIENT_SECRET}
      YOUTUBE_API_KEY: ${YOUTUBE_API_KEY}
      NEWSAPI_KEY: ${NEWSAPI_KEY}
      TIME_ZONE: Asia/Seoul
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    command: python manage.py runserver 0.0.0.0:8000

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_BASE_URL: http://localhost:8000/api
    command: pnpm dev --host 0.0.0.0

volumes:
  db_data:
```

### 4.2 사용
```bash
# 최초 실행
cp .env.example .env   # 환경변수 채우기
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py loaddata seed_industries.json

# 수집 수동 실행
docker compose exec backend python manage.py run_collection

# 접속
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/api
```

### 4.3 MariaDB 사용 시 주의
- Django의 `mysqlclient` 패키지 필요 → `backend/Dockerfile`에 빌드 의존성 (`default-libmysqlclient-dev`, `pkg-config`, `gcc`) 설치
- `utf8mb4` 강제 설정 (이모지/일본어/중국어 콘텐츠 대비):
  ```python
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.mysql",
          "OPTIONS": {"charset": "utf8mb4"},
          ...
      }
  }
  ```

---

## 5. 데이터 모델 (ERD)

### 5.1 핵심 엔티티

```
Industry (업종)
  id, name, slug, is_active, sort_order, created_at

Keyword (키워드)
  id, industry (FK), term, weight (default=1), is_active

Source (출처)
  id, name, slug, type [news|video|search_trend|sns], is_active

ContentItem (수집된 콘텐츠) -- 통합 테이블
  id
  source (FK)
  external_id              # 원본 식별자
  title (varchar 500)
  url (varchar 1000)
  thumbnail_url (nullable)
  published_at
  collected_at
  raw_content (LONGTEXT)
  metadata (JSON)
  industries (M2M → Industry)
  is_pinned (bool)
  llm_summary (TEXT, nullable)

TrendKeyword
  id, source (FK), keyword, rank, observed_at, metadata (JSON)
  industries (M2M, nullable)

CollectionRun
  id, source (FK), started_at, finished_at,
  status [success|partial|failed], error_message, items_collected
```

### 5.2 인덱스
- `ContentItem(published_at)`, `ContentItem(collected_at)`
- `(source_id, external_id)` UNIQUE
- `Industry(slug)` UNIQUE
- `TrendKeyword(observed_at, source_id)`

---

## 6. 데이터 수집 명세

### 6.1 Collector 인터페이스

```python
class BaseCollector(ABC):
    source_slug: str

    @abstractmethod
    def collect(self, run_date: date) -> list[dict]: ...

    @abstractmethod
    def health_check(self) -> bool: ...
```

### 6.2 소스별 수집 정책

| 소스 | 대상 | 수집량 | API 키 | 비용 |
|------|------|--------|--------|------|
| 네이버 뉴스 검색 API | 업종 키워드별 24h 기사 | 업종당 상위 10건 | Client ID/Secret | 무료 (25,000건/일) |
| 네이버 DataLab | 업종 키워드 검색량 추이 | 일별 | 동일 | 무료 |
| YouTube Data API v3 | 한국 인기 동영상 + 업종 키워드 | 인기 20 + 업종당 5 | API Key | 무료 (quota 10,000/일) |
| NewsAPI / RSS | 일반 헤드라인 | 상위 20 | NewsAPI 키 (RSS는 불필요) | NewsAPI 무료 100req/일 |

### 6.3 분류 (MVP)
1. **키워드 매칭**: `Industry.keywords`에 등록된 term이 제목/본문에 포함되면 해당 업종 태깅 (다중 가능)
2. **LLM 분류**: 인터페이스만 존재, 실제 호출 X (Phase 2)

---

## 7. 화면 / 라우팅

### 7.1 React 페이지 라우트

| 경로 | 컴포넌트 | 설명 |
|------|---------|------|
| `/` | `Dashboard` | 오늘의 대시보드 |
| `/?date=YYYY-MM-DD` | `Dashboard` | 특정 날짜 |
| `/archive` | `Archive` | 날짜별 아카이브 (캘린더 + 리스트) |
| `/industries/:slug` | `IndustryDetail` | 업종별 누적 콘텐츠 |
| `/admin` | `AdminLayout` | 관리자 레이아웃 |
| `/admin/industries` | `IndustriesPage` | 업종 CRUD |
| `/admin/keywords` | `KeywordsPage` | 키워드 CRUD |
| `/admin/sources` | `SourcesPage` | 소스 활성화/비활성화 |
| `/admin/runs` | `CollectionRunsPage` | 수집 로그 + 수동 트리거 버튼 |

### 7.2 메인 대시보드 (`/`)

```
┌──────────────────────────────────────────────────────────────┐
│  📈 MarketingPulse        [📅 2026-04-27 ▼]  [Admin →]      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  📰 오늘의 핫이슈 (일반 뉴스)                                 │
│  ─ 기사1 제목                            [원문 →]            │
│  ─ 기사2 제목                            [원문 →]            │
│                                                              │
│  🔥 플랫폼별 트렌드                                           │
│  ┌─ 네이버 검색 ─┬─ YouTube 인기 ─┐                         │
│  │ 1. 키워드A    │ 1. 동영상X     │                         │
│  └───────────────┴────────────────┘                         │
│                                                              │
│  🏷️ 업종별  [전체|법률|병원|의류|숙박|식당]                  │
│  ─ [법률] 콘텐츠 카드                    [원문 →]            │
│  ─ [병원] 콘텐츠 카드                    [원문 →]            │
└──────────────────────────────────────────────────────────────┘
```

### 7.3 Admin 페이지 패턴 (공통)
- shadcn/ui의 `Table` + `Dialog` + `Form` 조합
- 좌측 사이드바: 메뉴 (Industries / Keywords / Sources / Runs)
- 상단 우측: "추가" 버튼 → Dialog 모달
- 행 우측: 수정 / 삭제 액션
- TanStack Query의 `useMutation` + `invalidateQueries`로 갱신

---

## 8. API 엔드포인트 (DRF)

### 8.1 공개 API (대시보드용)
```
GET  /api/dashboard/?date=YYYY-MM-DD&industry=<slug>
     → { news: [...], trends: {...}, by_industry: {...} }

GET  /api/content/?date=...&industry=...&source=...&page=1
     → 페이징된 ContentItem 목록

GET  /api/trends/?date=...&source=naver_search
     → TrendKeyword 목록

GET  /api/industries/
     → 활성 업종 목록 (필터 셀렉터용)
```

### 8.2 Admin API (인증 필요)
```
# Industries
GET    /api/admin/industries/
POST   /api/admin/industries/
PATCH  /api/admin/industries/<id>/
DELETE /api/admin/industries/<id>/

# Keywords (동일 패턴)
GET/POST/PATCH/DELETE /api/admin/keywords/

# Sources
GET/PATCH /api/admin/sources/

# Collection Runs
GET  /api/admin/runs/
POST /api/admin/runs/trigger/   → 수동 수집 시작

# Health
GET  /api/health/
```

### 8.3 인증 (MVP)
- DRF의 `TokenAuthentication` 또는 단순 `Authorization: Bearer <env에 박힌 토큰>` 헤더
- 회원가입/로그인 UI는 만들지 않음. Admin 페이지에 토큰 입력 필드 1개만.
- Phase 2에서 정식 로그인 도입.

---

## 9. LLM 연동 (Skeleton)

```python
# backend/apps/llm/base.py
class LLMProvider(ABC):
    @abstractmethod
    def summarize(self, text: str, max_tokens: int = 200) -> str: ...

    @abstractmethod
    def classify_industry(self, text: str, industries: list[str]) -> list[str]: ...

# backend/apps/llm/providers/claude.py  (스텁)
class ClaudeProvider(LLMProvider):
    def summarize(self, text, max_tokens=200):
        raise NotImplementedError("Phase 2")
```

- 환경변수 `LLM_PROVIDER`, `LLM_API_KEY` 자리는 settings에 미리 정의
- Phase 2에서 Provider 클래스만 채우면 동작

---

## 10. 스케줄링

### 10.1 정기 실행
- **매일 08:00 KST** — `python manage.py run_collection`
- 실패한 수집기는 로깅 후 다음 진행 (Fail-fast 금지)
- 결과는 `CollectionRun`에 기록

### 10.2 구현
- **로컬 (Docker Compose)**: `cron` 컨테이너를 추가하거나, 호스트 cron이 `docker compose exec backend ...` 호출
- **데모 배포**: Railway/Render의 Cron Jobs 기능 사용
- **수동 트리거**: Admin 페이지의 "수집 실행" 버튼 → `POST /api/admin/runs/trigger/`

---

## 11. 배포 / 운영

### 11.1 로컬 (메인 개발 환경)
- Docker Compose 1방으로 backend + frontend + db 모두 실행
- `http://localhost:5173` 에서 작업

### 11.2 데모 배포 (선택)
- 토요일 데모를 로컬에서 화면 공유로 진행한다면 배포 불필요
- 배포 원할 경우:
  - 옵션 A: **Railway** — Docker Compose 자동 인식, MariaDB 플러그인 있음
  - 옵션 B: **백엔드는 Railway/Render, 프론트엔드는 Vercel** 분리 배포

### 11.3 환경변수 (`.env.example`)
```
# DB
DB_NAME=marketing_pulse
DB_USER=mp_user
DB_PASSWORD=
DB_ROOT_PASSWORD=

# Django
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
ADMIN_API_TOKEN=

# 외부 API
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
YOUTUBE_API_KEY=
NEWSAPI_KEY=

# LLM (비활성)
LLM_PROVIDER=
LLM_API_KEY=

TIME_ZONE=Asia/Seoul
```

---

## 12. 일정 (이번 주 — 토요일 21시 데모 기준)

> ⚠️ React로 Admin까지 직접 만들기로 한 만큼 일정이 빡빡합니다. 우선순위는 **수집 → 대시보드 → Admin** 순. 시간 부족 시 Admin은 핵심 CRUD(업종/키워드)만 살리고 나머지는 Django Admin 임시 노출로 대체.

| 일자 | 작업 |
|------|------|
| **D-1 (월)** | Docker Compose 골격, Django + DRF 초기화, MariaDB 연결, 모델 정의/마이그레이션, 시드 데이터 |
| **D-2 (화)** | Collector 4종 구현 (네이버 뉴스/DataLab/YouTube/NewsAPI), `run_collection` 명령, 키워드 분류기 |
| **D-3 (수)** | Public API 엔드포인트 + Admin API 엔드포인트, 토큰 인증, Vite + React + Tailwind + shadcn/ui 셋업 |
| **D-4 (목)** | 메인 대시보드 페이지 (날짜/업종 필터), 업종별 상세, 아카이브 |
| **D-5 (금)** | Admin: Industries / Keywords CRUD, Sources / Runs 페이지 |
| **D-6 (토)** | 스케줄링 동작 확인, 버그픽스, 데모 시나리오 리허설, 21시 데모 |

> **버퍼**: 거의 없음. D-3까지 일정 밀리면 Admin 페이지 일부를 Django Admin 임시 사용으로 폴백할 것.

---

## 13. Phase 2 로드맵

| 우선순위 | 항목 |
|---------|------|
| 1 | LLM 요약/자동 분류 활성화 (Claude API) |
| 2 | 이메일/슬랙 푸시 알림 (오전 8:30 발송) |
| 3 | 인스타그램 / 틱톡 / X 데이터 (Apify, Bright Data 등 검토) |
| 4 | 차트/그래프 시각화 (Recharts 등) |
| 5 | 정식 사용자 인증 / 멀티 테넌시 |
| 6 | 외부 SaaS 화 (결제/플랜/온보딩) |

---

## 14. 리스크 & 가정

### 리스크
| 항목 | 영향 | 대응 |
|------|------|------|
| Admin React 페이지 일정 초과 | 데모 일부 누락 | Django Admin 임시 노출로 폴백 |
| 네이버/YouTube API 한도 초과 | 수집 실패 | 업종/키워드 수 제한, 캐싱 |
| 키워드 분류기 정확도 낮음 | 잘못된 업종 노출 | MVP 한계로 인정. Phase 2 LLM 보강 |
| MariaDB-Django 호환 이슈 | 빌드 실패 | `mysqlclient` + `default-libmysqlclient-dev` Dockerfile 명시 |
| 토요일 일정 빠듯 | 부분 미완성 | "파이프라인 동작" 우선, UI 미려함 후순위 |

### 가정
- 클라이언트가 네이버/YouTube/NewsAPI 키 발급
- 데모는 로컬 화면 공유 또는 임시 배포 중 1택
- 한국 시장 한정

---

## 15. 데모 시 보여줄 것 (토요일 21시)

1. `docker compose up` 으로 전체 스택 부팅 시연 (또는 사전에 띄워둠)
2. **대시보드** 접속 → 오늘 데이터 확인
3. 날짜 변경 → 어제/그제 데이터 확인
4. 업종 필터 → 5개 업종 각각 확인
5. **Admin 페이지** → 업종 추가 (예: "반려동물") → 키워드 등록 → 수동 수집 트리거 → 새 업종에 콘텐츠 잡히는지 확인
6. 코드 구조 설명 — Collector 인터페이스, LLM skeleton, 확장 포인트
7. Phase 2 로드맵 공유

---

## 16. 클라이언트 확정 필요 사항

> 작업 시작 전에 배대근 님께 확인.

- [ ] API 키 발급 주체 (네이버 / YouTube / NewsAPI)
- [ ] 5개 업종별 **시드 키워드 리스트** (예: 법률 → "변호사", "법률사무소", "리걸테크" ...)
- [ ] 데모 방식: 로컬 화면 공유 vs 임시 배포 URL
- [ ] 토요일 21시 데모 채널 (Zoom/Google Meet)
- [ ] Admin 토큰 공유 방식 (1Password 등)
