# MarketingPulse — 개발 현황 보고서

> **작성일**: 2026-04-28
> **버전**: MVP v0.3
> **개발 기간**: 1일 (집중 개발)
> **상태**: 동작 가능한 데모 (로컬)

---

## 1. 한 줄 요약

**매일 아침 마케팅 담당자가 한 페이지에서 핵심 트렌드/이슈/뉴스를 확인할 수 있는 대시보드**가 동작 가능한 상태로 구축되었습니다. 5개 업종(법률/병원/의류/숙박/식당) × 90개 키워드 기반으로 네이버 뉴스, 네이버 DataLab 검색 트렌드, YouTube 마케팅 영상, Google News RSS, 큐레이션 유튜브 채널 등 5개 소스를 매일 자동 수집·분류·표시합니다.

---

## 2. 시스템 구성

```
┌──────────────────────────────────────────────────────────────────┐
│ Frontend (호스트 Node + npm)                                     │
│ React 18 + Vite + TypeScript + Tailwind + shadcn/ui              │
│ http://localhost:5173                                            │
└──────────────────────┬───────────────────────────────────────────┘
                       │ /api  (axios + TanStack Query)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│ Backend (Docker)                                                 │
│ Django 5 + DRF + httpx                                           │
│ http://localhost:8181/api                                        │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                      │
│  │  Public API     │    │  Admin API      │                      │
│  │  /dashboard/    │    │  /admin/...     │                      │
│  │  /content/      │    │  Bearer Token   │                      │
│  │  /trends/       │    │  단일 토큰 인증   │                      │
│  └─────────────────┘    └─────────────────┘                      │
│                       ▲                                          │
└───────────────────────┼──────────────────────────────────────────┘
                        │ ORM
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│ MariaDB 11 (Docker)                                              │
│ Industry / Keyword / Source / ContentItem / TrendKeyword /       │
│ CollectionRun / CuratedChannel                                   │
└──────────────────────────────────────────────────────────────────┘
                        ▲
                        │
        ┌───────────────┴───────────────┐
        │                               │
   [매일 1회 수집 — make collect / 또는 cron]
        │
        ├── Naver News API (네이버 뉴스 검색)
        ├── Naver DataLab API (검색 트렌드)
        ├── YouTube Data API v3 (영상 + 큐레이션 채널)
        ├── Google News RSS (마케팅 토픽 검색)
        └── NewsAPI (RSS 폴백)
```

---

## 3. 현재 가능한 것 (✅ MVP에 포함됨)

### 3.1 데이터 수집 (5개 소스, 자동)

| 소스 | 수집 내용 | 일평균 결과 (오늘 기준) | 비용 |
|------|-----------|---------------------|------|
| **네이버 뉴스 API** | 90개 키워드 × 24h 기사 (업종당 5-10건) | ~390건 | 무료 (25,000건/일) |
| **네이버 DataLab API** | 90개 키워드의 7일 검색량 → ratio 정렬 → TOP 30 | 30건 | 무료 (1,000건/일) |
| **YouTube Data API v3 (마케팅 영상)** | "마케팅 사례/트렌드/전략" phrase + 조회수순 + 업종별 키워드 검색 | ~40건 | 무료 (10,000 quota/일, 600 사용) |
| **YouTube Data API v3 (큐레이션 채널)** | Admin에서 등록한 채널의 최신 영상 3건씩 | 채널 × 3 | 무료 (~5 quota/채널) |
| **Google News RSS** (1순위) | "마케팅/광고/브랜드/트렌드" 검색 결과 | 20건 | **무제한, 키 불필요** |
| ~~NewsAPI~~ (RSS 실패 시 폴백) | top-headlines | RSS가 살아있으면 호출 X | 무료 100req/일 |

총 일일 수집량: **~480건 콘텐츠 + 30개 트렌드 키워드** (오늘 기준 측정)

### 3.2 분류 / 정렬

- **키워드 매칭 분류기** (`apps.classifier`): ContentItem.title + raw_content에서 90개 키워드 substring 매칭 → 업종 자동 태깅 (다중 가능)
- **YouTube 영상 직접 매핑**: 업종별 검색 결과는 `metadata.industry_slug`로 강제 태깅 (키워드 매칭 누락 방지)
- **TrendKeyword 순위**: DataLab 그룹별 7일 평균 ratio 내림차순

### 3.3 대시보드 페이지 (사용자용)

| 섹션 | 내용 | 출처 |
|------|------|------|
| 📰 **오늘의 핫이슈** | 마케팅 토픽 뉴스 10건 (자동 필터링) | Google News RSS 마케팅 검색 |
| 🔥 **네이버 검색 TOP 10** | 검색량 ratio 기반 키워드 순위 + 매칭 업종 뱃지 | DataLab |
| 🎬 **오늘의 마케팅 영상 TOP** | 마케팅 phrase × 조회수순 영상 6건 (썸네일) | YouTube search |
| 🎙️ **마케팅 채널 신규** | 큐레이션 채널 최신 영상 6건 (썸네일) | YouTube channels |
| 🏷️ **업종별 카드 (5개)** | 업종별 뉴스 + 영상 혼합 5건씩 | 분류기 + YouTube 직접 매핑 |
| 📅 **날짜 네비게이터** | 과거 날짜 조회 가능 | DB 누적 |

추가 페이지: `/archive` (최근 30일), `/industries/:slug` (업종별 누적)

### 3.4 Admin 페이지 (내부 운영)

토큰 기반 인증 (`Authorization: Bearer <ADMIN_API_TOKEN>`).

| 페이지 | 기능 |
|--------|------|
| `/admin/industries` | 업종 추가/수정/삭제, 활성/비활성, 정렬 순서 |
| `/admin/keywords` | 업종별 카드 그리드, 키워드 칩 추가/삭제/가중치 수정/활성토글 |
| `/admin/sources` | 5개 소스 활성/비활성 토글 |
| `/admin/channels` | YouTube 큐레이션 채널 등록 (`@핸들` 또는 `UCxxx` ID) |
| `/admin/runs` | 최근 50건 수집 로그 + "수동 수집 실행" 버튼 |

### 3.5 인프라 / 배포

- **Backend + DB**: Docker Compose 1방으로 부팅 — `cd backend && make init`
- **Frontend**: 호스트 npm — `cd frontend && npm install && npm run dev`
- **포트 충돌 자동 회피**: 호스트의 다른 docker 프로젝트 고려해 8181/5173 사용
- **DB 볼륨 영속**: `name: marketingtrends`로 명시 → 컨테이너 재생성해도 데이터 보존
- **Mock 폴백**: 외부 API 키 없어도 모든 collector가 mock 데이터로 동작

### 3.6 운영 도구

```bash
make init      # build + up + migrate + seed + collect
make collect   # 수집 1회
make logs      # 로그 follow
make health    # health check
make test-api  # 공개/admin 엔드포인트 동작 확인
make nuke      # 컨테이너 + DB 전부 제거
```

---

## 4. 현재 불가능한 것 (❌ MVP에서 제외 / 한계)

### 4.1 데이터 소스 (Phase 2 예정)

| 항목 | 이유 / 한계 |
|------|------------|
| **인스타그램 트렌드** | 공식 API 매우 제한적. Apify, Bright Data 등 유료 스크래핑 솔루션 필요 |
| **틱톡 트렌드** | 공식 API 제한적. 동일하게 유료 도구 또는 비공식 라이브러리 |
| **X (트위터) 트렌드** | API v2 유료화 ($100+/월). Tweetdeck 스크래핑 또는 Brandwatch 등 |
| **유튜브 검색 트렌드** | YouTube는 검색량 트렌드 API를 공식 제공 안 함 (Google Trends는 가능) |

### 4.2 LLM 기능 (인터페이스만 존재, 실제 호출 X)

| 항목 | 현재 상태 |
|------|----------|
| **자동 요약** | `apps.llm.base.LLMProvider.summarize` 추상 메서드 정의됨, `ClaudeProvider`는 `NotImplementedError` |
| **자동 업종 분류** | `classify_industry` 추상 메서드만. 현재는 keyword substring 매칭만 작동 |
| **콘텐츠 카테고리화** ("성공사례" vs 단순 뉴스) | 미구현 |
| **인사이트 생성** ("오늘 가장 주목할 트렌드 3가지") | 미구현 |

### 4.3 알림 / 외부 발송

- **이메일 알림** 미구현
- **슬랙 알림** 미구현
- **카카오톡/디스코드** 미구현
- **푸시 알림** 미구현

### 4.4 시각화

- **차트/그래프** 없음 (텍스트 리스트 + 썸네일만)
- **트렌드 시계열 차트** 없음 (DataLab 7일 추이 데이터는 메타에 있지만 표시 안 함)
- **워드클라우드** 없음

### 4.5 사용자 / 인증

- **회원가입 / 로그인 UI** 없음 (단일 admin 토큰만)
- **권한 분리** 없음 (admin = all)
- **다중 사용자 / 멀티 테넌시** 없음
- **개인화 (관심 업종 저장 등)** 없음

### 4.6 운영 자동화

- **자동 스케줄링** 미구현 — 현재는 `make collect` 수동 또는 외부 cron 등록 필요
  - Phase 2: 호스트 cron / Docker cron 컨테이너 / Railway Cron Jobs 중 선택
- **에러 알림** 미구현 (실패 시 admin /runs 페이지에 표시만)
- **모니터링/메트릭** 미구현

### 4.7 데이터 정확도 한계

| 항목 | 한계 |
|------|------|
| **DataLab ratio 절대 비교** | 호출 내 max=100 정규화이라 다른 chunk 키워드와 직접 비교 부정확. 정확하려면 anchor 키워드 도입 필요 (Phase 2) |
| **YouTube 조회수 정렬** | 검색 결과 내 조회수 순. 진짜 조회수 1위가 아닐 수 있음. `videos.list?part=statistics` 추가 호출로 정확화 가능 (quota +) |
| **키워드 매칭 분류 정확도** | substring 단순 매칭이라 "변호사 광고 규제"가 의류 카테고리(키워드: "광고")에 매칭 가능. LLM 분류로만 해결 |
| **마케팅 영상 TOP 후보 수** | phrase 검색이 좁아 결과 4-8건. 단어 검색하면 noise 증가. trade-off |

### 4.8 외부 API 의존

| API | 한도 | 한도 도달 시 |
|-----|------|--------------|
| YouTube Data API v3 | 10,000 quota/일 | 차단 → quota 회복 (PT 자정) 또는 추가 GCP 프로젝트 |
| 네이버 검색 API | 25,000건/일 | 차단 — 90개 키워드 × 1회 = 90건이라 여유 |
| 네이버 DataLab | 1,000건/일 | 차단 — 18 호출이라 여유 |
| **Google News RSS** (현재 운영 중) | 무제한, 키 불필요 | 영향 없음 |
| ~~NewsAPI~~ | RSS 실패 시 폴백만, 평소엔 호출 X | NewsAPI 자체에 의존하지 않음 |

### 4.9 모바일

- **반응형 기본만 적용** (Tailwind grid 컬럼 변경)
- **모바일 전용 UI** 없음 (햄버거 메뉴, 스와이프 등)
- **PWA** 아님

---

## 5. 확장 가능성 (Phase 2 / Phase 3 로드맵)

### 5.1 Phase 2 (단기, 1-2주)

| 우선순위 | 항목 | 작업 분량 | 효과 |
|---------|------|----------|------|
| ⭐⭐⭐ | **LLM 활성화 (Claude API)** — `ClaudeProvider` 구현, ContentItem.llm_summary 채우기, 자동 카테고리 분류 | 1-2일 | 콘텐츠 품질 ↑↑ ("성공사례" vs "단순 뉴스" 구분 등) |
| ⭐⭐⭐ | **이메일 발송** — 매일 오전 8:30 SendGrid/AWS SES 연동, 핵심 5건 + 업종별 1건씩 | 1일 | "받아보는 형태" 가치 |
| ⭐⭐ | **슬랙 webhook** — 사내 마케팅 채널에 매일 푸시 | 0.5일 | 팀 공유 |
| ⭐⭐ | **자동 스케줄링** — Docker cron 컨테이너 또는 호스트 cron 등록 | 0.5일 | 진짜 "매일 자동" |
| ⭐⭐ | **DataLab anchor 정규화** — 모든 chunk에 공통 anchor 키워드 포함, 절대 검색량 비교 가능하게 | 0.5일 | 트렌드 순위 정확도 |
| ⭐⭐ | **YouTube viewCount 정확화** — `videos.list?part=statistics` 추가 호출, metadata에 viewCount 저장, 그 기준 정렬 | 0.5일 | 진짜 조회수 TOP |
| ⭐ | **차트/그래프** — Recharts로 트렌드 시계열, 업종별 콘텐츠 수 추이 등 | 1일 | 시각적 임팩트 |

### 5.2 Phase 3 (중기, 1-2개월)

| 항목 | 도구 후보 | 설명 |
|------|----------|------|
| **인스타그램 / 틱톡 / X 데이터** | Apify, Bright Data, ScrapingBee | 유료 스크래핑 솔루션 활용 |
| **정식 사용자 인증** | Django allauth, Auth0 | 회원가입/로그인, 비번 리셋 |
| **개인화** | User 모델 + UserPreference | 사용자별 관심 업종, 즐겨찾기 콘텐츠 |
| **북마크 / 메모** | ContentItem에 User M2M 추가 | 콘텐츠에 메모 달기, 모음 |
| **검색** | Postgres FTS 또는 Elasticsearch | 누적 콘텐츠 전체 검색 |
| **모바일 PWA** | Vite PWA 플러그인 | 홈화면 추가, 오프라인 동작 |

### 5.3 Phase 4 (장기, SaaS화)

| 항목 | 비고 |
|------|------|
| **멀티 테넌시** | Workspace 모델 + 구독 플랜 (Free/Pro/Enterprise) |
| **결제 시스템** | Stripe / 토스페이먼츠 연동 |
| **온보딩 플로우** | 업종 선택 → 키워드 추천 → 첫 리포트 자동 생성 |
| **외부 데이터 마켓플레이스** | 다른 SaaS에 우리 데이터 API 판매 |
| **카테고리 확장** | 5개 업종 → 20+ 업종 (B2B SaaS, 부동산, 교육, 헬스케어 등) |
| **국제화** | 일본/미국 시장 — 각국 뉴스/검색 트렌드 API 연동 |

---

## 6. 코드 구조 요약 (확장 시 참고)

### 6.1 Backend 핵심 진입점

| 파일 | 역할 |
|------|------|
| `apps/collectors/base.py` | `BaseCollector` ABC — 새 수집기는 이걸 상속 |
| `apps/collectors/registry.py` | source.slug → Collector 클래스 매핑 (확장 시 한 줄 추가) |
| `apps/collectors/management/commands/run_collection.py` | 전체 수집 파이프라인 (모든 collector 순회) |
| `apps/classifier/keyword_matcher.py` | 분류 로직 (LLM으로 교체 가능) |
| `apps/llm/base.py` + `apps/llm/providers/claude.py` | LLM 추상 인터페이스 (Phase 2 활성화 지점) |
| `apps/dashboard/views.py` | 대시보드 응답 집계 |

### 6.2 새로운 수집기 추가 절차 (5분)

1. `apps/collectors/<new>.py` 작성 — `BaseCollector` 상속
2. `apps/collectors/registry.py`에 등록
3. `apps/collectors/management/commands/seed_data.py`의 `SOURCES`에 추가
4. `make seed` → `make collect`

### 6.3 새로운 LLM Provider 추가 절차

1. `apps/llm/providers/<new>.py` — `LLMProvider` 상속
2. `apps/llm/base.py`의 factory 등록 (또는 settings.LLM_PROVIDER로 선택)
3. `ContentItem.llm_summary` / `metadata` 채우는 로직을 `run_collection.py`에 추가

### 6.4 새로운 업종 추가 절차 (1분)

- Admin > Industries > "추가" 클릭 → 이름/slug 입력
- Admin > Keywords > 해당 업종 카드에 키워드 칩 추가
- 다음 수집부터 자동 분류

---

## 7. 외부 API 키 발급 비용 / 한도

| API | 발급처 | 무료 한도 | 한도 초과 시 비용 |
|-----|--------|----------|----------------|
| 네이버 (검색 + DataLab) | https://developers.naver.com/apps/ | 25,000건/일 (검색) + 1,000건/일 (DataLab) | 추가 API 신청 (무료 대부분) |
| YouTube Data API v3 | https://console.cloud.google.com | 10,000 quota/일 | $0.50 / 1,000,000 unit (실질 무료) |
| **Google News RSS** (현재 사용) | 발급 불필요 | 무제한 | 무료 |
| ~~NewsAPI~~ (선택, 폴백만) | https://newsapi.org | 100 req/일 (localhost 전용) | $449/월 (배포 시) — **현재 RSS만 사용해서 불필요** |
| Claude API (Phase 2) | https://console.anthropic.com | 첫 $5 크레딧 무료 | Sonnet 4.6: $3 / 1M input + $15 / 1M output |

**현재 운영 비용**: $0 / 월 (모든 무료 한도 내)
**Phase 2 LLM 활성화 시 예상**: 일 100건 콘텐츠 요약 = ~$1-3/월 (Claude Haiku 기준)

---

## 8. 배포 옵션 (선택)

| 옵션 | 비용 | 난이도 | 특징 |
|------|------|--------|------|
| **로컬 화면 공유로 데모** | $0 | ⭐ | 가장 빠름, 데모용 |
| **Railway** | ~$5-20/월 | ⭐⭐ | Docker Compose 자동 인식, MariaDB 플러그인 |
| **Backend = Render / Railway, Frontend = Vercel** | ~$5/월 | ⭐⭐ | 분리 배포 (성능 ↑) |
| **AWS ECS + RDS** | ~$30-100/월 | ⭐⭐⭐⭐ | 정식 운영, 확장성 |

---

## 9. 리스크 / 고려사항

| 항목 | 리스크 | 완화책 |
|------|--------|--------|
| **YouTube quota** | 디버깅 중 빨리 소진 (10K/일) | 운영에선 1일 1회 호출만 = 600 quota → 여유. 추가 GCP 프로젝트 키 보유 권장 |
| **네이버 API rate limit** | 동시 요청 시 429 발생 | 현재 throttle 0.15s 적용. 더 안정화하려면 sleep 늘리기 |
| **키워드 분류 정확도** | substring 매칭 한계 — 가짜 매칭 가능 | LLM 분류 도입 (Phase 2) |
| ~~NewsAPI 배포 비용~~ | (현재 RSS만 사용 중이라 N/A) | NewsAPI 키 자체가 운영에 필요 없음 |
| **마케팅 채널 큐레이션 품질** | 사용자가 직접 등록해야 함 | 추천 채널 가이드 제공, Admin UI에 검증 추가 가능 |
| **데이터 누적 부담** | 매일 ~480건 × 365일 = 175K | MariaDB로 충분, 1년 후 archival 정책 검토 |

---

## 10. 데모 시나리오 (보고용)

1. **`make init`** 으로 1분 만에 로컬 부팅
2. http://localhost:5173 → 메인 대시보드 진입
   - 핫이슈 10건 (마케팅 뉴스)
   - 네이버 검색 TOP 10 (배달의민족, 무신사, 부킹닷컴 등)
   - 마케팅 영상 TOP 6건 (썸네일)
   - 큐레이션 채널 신규 (EO Korea, 신사임당 등)
   - 업종별 5개 카드
3. **날짜 변경** → 어제/그제 데이터 (DB 누적 확인)
4. **업종 카드의 "더보기"** → 업종별 누적 페이지
5. **`/admin`** → 토큰 입력 → Industries / Keywords / Sources / YouTube 채널 / Runs
6. **Admin > Keywords**: 업종 카드 + 칩 UI로 90개 키워드 한눈에 관리
7. **Admin > Runs**: 5초 자동 갱신, "수동 수집 실행" 버튼 클릭 시연
8. **Phase 2 로드맵 공유** (위 §5)

---

## 11. 결론

### 11.1 현재 가치
- **5개 업종 × 90개 키워드의 마케팅 데이터를 매일 자동 수집**하고 한 페이지에서 확인 가능
- **운영 비용 $0** (모든 무료 한도 내)
- **확장 포인트가 명확**: collector 추가, LLM 활성화, 알림 추가가 각각 0.5-1일 작업

### 11.2 다음 단계 추천 (의사결정 필요)
1. **데모 후 즉시 실사용 진입 여부** 판단
2. **Phase 2 우선순위** 확정 (LLM, 알림, 새 채널 중 무엇부터?)
3. **배포 환경** 결정 (로컬 시연으로 충분 vs 임시 배포)
4. **외부 API 키 운영 주체** 확정 (현재 개발자 개인 키 사용 중)

### 11.3 가장 큰 비즈니스 가치
> "5개 업종, 90개 키워드, 5개 데이터 소스를 매일 일일이 확인하던 시간이 **5분으로 단축**" — 마케팅 담당자 1명 기준 하루 30-60분 절약.

---

**Appendix**
- 기술 명세: `plan.md`
- 실행 가이드: `README.md`, `backend/README.md`, `frontend/README.md`
- 코드: GitHub (별도 push 시)
