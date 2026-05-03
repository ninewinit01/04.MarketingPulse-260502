# MarketingPulse — Backend

Django 5 + DRF + MariaDB. Docker Compose로 운영. 전체 기획은 루트 `../plan.md` 참고.

## 빠른 시작

```bash
# 최초 1회: build + up + makemigrations + migrate + seed + collect
make init

# 그 후
make up           # 백그라운드 실행
make collect      # 수집 1회 더
make help         # 모든 명령
```

브라우저: http://localhost:8181/api/health/

## Makefile 명령

| 명령 | 설명 |
|------|------|
| `make help` | 전체 명령 목록 |
| `make init` | 처음부터 끝까지 (build → migrate → seed → collect) |
| `make up` / `make down` | 컨테이너 실행/중지 |
| `make build` / `make up-build` | 이미지 빌드 |
| `make restart` | backend 재시작 (`.env` 변경 후) |
| `make logs` / `make logs-backend` / `make logs-db` | 로그 follow |
| `make migrate` / `make makemigrations` | DB 스키마 |
| `make seed` | 5 업종 + 25 키워드 + 4 source 시드 |
| `make collect` | 수집 1회 |
| `make superuser` | Django Admin 계정 생성 |
| `make shell` / `make dbshell` | Django shell / MariaDB CLI |
| `make health` / `make test-api` | API 동작 확인 |
| `make bash` | backend 컨테이너 셸 |
| `make nuke` | 컨테이너 + DB 볼륨 전부 제거 |
| `make reset` | nuke + init |

## 디렉터리

```
backend/
├── Dockerfile
├── docker-compose.yml          # name: marketingtrends, db + backend
├── docker-compose.override.yml # 로컬 dev: 소스 마운트 + DEBUG
├── Makefile
├── .env / .env.example
├── pyproject.toml
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py             # MariaDB, DRF, CORS, ADMIN_API_TOKEN
│   │   ├── dev.py              # DEBUG=True, CORS 전체 허용
│   │   └── prod.py
│   ├── urls.py                 # /api/ 루트 라우터
│   ├── wsgi.py / asgi.py
└── apps/
    ├── core/                   # ADMIN_API_TOKEN 인증, /api/health/
    ├── industries/             # Industry, Keyword (모델 + DRF)
    ├── content/                # Source, ContentItem, TrendKeyword, CollectionRun
    ├── classifier/             # 키워드 → 업종 매칭 (substring)
    ├── collectors/             # 4개 collector + run_collection / seed_data 명령
    │   ├── base.py
    │   ├── registry.py
    │   ├── naver_news.py
    │   ├── naver_datalab.py
    │   ├── youtube.py
    │   ├── news_rss.py
    │   ├── mocks.py            # API 키 없을 때 폴백 데이터
    │   └── management/commands/
    ├── dashboard/              # /api/dashboard/ 집계
    └── llm/                    # LLMProvider 추상 (Phase 2 스텁)
```

## API 엔드포인트

### Public (인증 불필요)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/health/` | health check |
| GET | `/api/dashboard/?date=YYYY-MM-DD&industry=<slug>` | 대시보드용 통합 JSON |
| GET | `/api/industries/` | 활성 업종 목록 |
| GET | `/api/content/?date=&industry=&source=` | 콘텐츠 페이징 |
| GET | `/api/trends/?date=&source=` | 트렌드 키워드 |

### Admin (`Authorization: Bearer <ADMIN_API_TOKEN>`)

| Method | Path | 설명 |
|--------|------|------|
| GET/POST/PATCH/DELETE | `/api/admin/industries/` | 업종 CRUD |
| GET/POST/PATCH/DELETE | `/api/admin/keywords/?industry=<id>` | 키워드 CRUD |
| GET/PATCH | `/api/admin/sources/` | 소스 활성화 토글 |
| GET | `/api/admin/runs/` | 최근 수집 로그 |
| POST | `/api/admin/runs/trigger/` | 수동 수집 (동기) |

## 환경 변수 (`.env`)

```
DB_NAME / DB_USER / DB_PASSWORD / DB_ROOT_PASSWORD
DJANGO_SECRET_KEY / DJANGO_DEBUG / DJANGO_ALLOWED_HOSTS
ADMIN_API_TOKEN                            # 단일 토큰
NAVER_CLIENT_ID / NAVER_CLIENT_SECRET      # 비워두면 mock
YOUTUBE_API_KEY                            # 비워두면 mock
NEWSAPI_KEY                                # 비워두면 Google News RSS 폴백
LLM_PROVIDER / LLM_API_KEY                 # Phase 2
TIME_ZONE=Asia/Seoul
```

키 없어도 mock 데이터로 전체 파이프라인 동작합니다.

## 외부 API 키 발급

| 변수 | 발급처 |
|------|--------|
| `NAVER_*` | https://developers.naver.com/apps/ — "검색" + "데이터랩" 둘 다 체크 |
| `YOUTUBE_API_KEY` | Google Cloud Console → API/서비스 → "YouTube Data API v3" 사용 설정 → API 키 생성 |
| `NEWSAPI_KEY` | https://newsapi.org/register (선택, 없으면 RSS 폴백) |

`.env` 채운 후 `make restart && make collect`.

## Collector 추가

1. `apps/collectors/<new_source>.py` 작성 — `BaseCollector` 상속, `collect(run_date)` 구현
2. `apps/collectors/registry.py` 의 `REGISTRY` dict에 등록
3. `apps/collectors/management/commands/seed_data.py` 의 `SOURCES` 에 추가
4. `make seed` → `make collect`

## 트러블슈팅

- **포트 충돌 (8181)**: 호스트에 다른 서비스가 8181을 잡고 있다면 `docker-compose.yml`의 `ports: 8181:8000`과 `../frontend/.env`의 `VITE_API_BASE_URL`을 동시에 변경.
- **DB 연결 실패**: `make logs-db` 로 MariaDB 부팅 확인. 실패면 `make nuke` 후 `make init`.
- **마이그레이션 충돌**: `make nuke && make init` 으로 전체 초기화.
- **`makemigrations`가 "No changes"**: Django가 앱 라벨을 못 찾는 경우 — `make makemigrations` (Makefile 안에서 명시적으로 앱 라벨 6개를 인자로 전달함).
