# MarketingPulse — Frontend

React 18 + Vite + TypeScript + Tailwind + shadcn/ui. 호스트 Node에서 직접 실행 (docker 안 씀).

## 빠른 시작

```bash
cp .env.example .env       # VITE_API_BASE_URL 확인 (기본: http://localhost:8181/api)
npm install                # 최초 1회
npm run dev                # http://localhost:5173 (점유 시 5174 등 자동)
```

> Backend가 먼저 떠 있어야 합니다. `cd ../backend && make up`.

## 스크립트

| 명령 | 설명 |
|------|------|
| `npm run dev` | Vite 개발 서버 (HMR) |
| `npm run build` | 프로덕션 빌드 (`tsc && vite build`) |
| `npm run preview` | 빌드 결과 로컬 프리뷰 |
| `npm run lint` | TypeScript 타입 체크 (`tsc --noEmit`) |

## 디렉터리

```
frontend/
├── package.json
├── vite.config.ts            # @/ alias = src/
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── .env / .env.example       # VITE_API_BASE_URL
└── src/
    ├── main.tsx              # QueryClient + BrowserRouter 셋업
    ├── App.tsx               # React Router 라우팅
    ├── index.css             # Tailwind directives + CSS 변수
    ├── lib/
    │   ├── api.ts            # axios 인스턴스 + 토큰 인터셉터
    │   ├── queries.ts        # TanStack Query 훅 모음
    │   └── utils.ts          # cn(), formatDate(), todayISO()
    ├── components/
    │   ├── ui/               # shadcn/ui (button/card/table/dialog/input/label/select/badge)
    │   ├── DateNavigator.tsx
    │   ├── IndustryFilter.tsx
    │   ├── ContentList.tsx
    │   ├── TrendList.tsx
    │   └── AdminLayout.tsx   # Admin 페이지 사이드바 + 토큰 입력
    ├── pages/
    │   ├── Dashboard.tsx     # /
    │   ├── Archive.tsx       # /archive
    │   ├── IndustryDetail.tsx# /industries/:slug
    │   └── admin/
    │       ├── IndustriesPage.tsx
    │       ├── KeywordsPage.tsx
    │       ├── SourcesPage.tsx
    │       └── CollectionRunsPage.tsx
    └── types/
        └── api.ts            # 백엔드 응답 타입 정의
```

## 라우트

| Path | Component |
|------|-----------|
| `/` | Dashboard (오늘의 트렌드 + 업종별) |
| `/?date=YYYY-MM-DD&industry=<slug>` | Dashboard (날짜/업종 필터) |
| `/archive` | 최근 30일 날짜 그리드 |
| `/industries/:slug` | 업종별 누적 콘텐츠 |
| `/admin` | Admin 레이아웃 (사이드바 + 토큰 입력) |
| `/admin/industries` | 업종 CRUD |
| `/admin/keywords` | 키워드 CRUD (업종별 필터) |
| `/admin/sources` | 소스 활성/비활성 토글 |
| `/admin/runs` | 수집 로그 + 수동 트리거 |

## Admin 사용법

1. http://localhost:5173/admin 접속
2. 좌측 토큰 입력 칸에 `backend/.env` 의 `ADMIN_API_TOKEN` 값 붙여넣기 → 저장 (페이지 리로드)
3. localStorage에 토큰 저장됨 — `/admin/*` 요청에 자동으로 `Authorization: Bearer <token>` 헤더 첨부
4. 토큰 잘못이면 모든 admin 요청이 401/403 — 토큰 다시 입력

## 환경 변수 (`.env`)

```
VITE_API_BASE_URL=http://localhost:8181/api
```

Backend 포트가 다르면 위 값 변경 → Vite 재시작 (`Ctrl+C` 후 `npm run dev`).

## 새 페이지 추가

1. `src/pages/<NewPage>.tsx` 생성
2. `src/App.tsx` 의 `<Routes>` 안에 `<Route>` 추가
3. 데이터 페칭이 필요하면 `src/lib/queries.ts` 에 훅 추가 (TanStack Query)

## 새 shadcn/ui 컴포넌트 추가

shadcn CLI를 안 쓰는 구조입니다. 필요한 컴포넌트는 https://ui.shadcn.com/docs/components 에서 코드 복사 → `src/components/ui/<name>.tsx` 로 직접 생성. Radix 의존성은 `package.json`에 추가.

## 트러블슈팅

- **`vite: command not found`**: `npm install` 안 했음. 프로젝트 디렉터리에서 한 번 실행.
- **CORS 에러**: backend의 `CORS_ALLOWED_ORIGINS` 에 현재 frontend origin이 포함됐는지 확인 (`backend/config/settings/base.py`). dev 모드에선 전체 허용이라 문제 없을 것.
- **Admin 페이지 401/403**: 토큰 잘못 입력. localStorage 비우고 다시 입력 (`localStorage.removeItem("admin_token")`).
- **포트 5173 점유**: Vite가 자동으로 5174, 5175...로 올라감. CORS 허용 목록에 5174까지 들어있으니 그대로 동작.
- **타입 에러**: `npm run lint` 로 확인.
