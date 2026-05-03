# DEPLOY — 배포 가이드

3가지 시나리오:

| 옵션 | 용도 | 난이도 | 도메인 | HTTPS |
|------|------|--------|--------|-------|
| **A. 로컬 PC** | 개발 / 시연 | ⭐ | ❌ | ❌ |
| **B. 홈서버 LAN** | 사내/가정 사용 | ⭐⭐ | ❌ (LAN IP) | ❌ (HTTP) |
| **C. 도메인 + HTTPS** | 정식 운영 | ⭐⭐⭐ | ✅ | ✅ |

각 옵션은 상위 옵션의 사전 조건. C로 가려면 A→B→C 순으로 검증 권장.

---

## A. 로컬 PC (개발 / 시연)

### 1. 사전 준비
- Docker Desktop (또는 Docker Engine + Compose v2)
- Node 20+
- (선택) 외부 API 키

### 2. Backend
```bash
cd backend
cp .env.example .env
```

`.env` 편집:
```
DB_NAME=marketing_pulse
DB_USER=mp_user
DB_PASSWORD=$(openssl rand -hex 16)        # 직접 생성
DB_ROOT_PASSWORD=$(openssl rand -hex 16)
DJANGO_SECRET_KEY=$(openssl rand -base64 50)
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
ADMIN_API_TOKEN=$(openssl rand -hex 32)
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
YOUTUBE_API_KEY=
NEWSAPI_KEY=
TIME_ZONE=Asia/Seoul
```
> 실제로는 `$(...)` 직접 실행해서 결과 값을 입력. `openssl` 없으면 https://www.random.org/ 등으로 임의 강한 문자열.

```bash
make init
# build + migrate + seed + 첫 수집까지 자동
```

### 3. Frontend
```bash
cd frontend
cp .env.example .env
# 안에 VITE_API_BASE_URL=http://localhost:8181/api 확인
npm install
npm run dev
```

### 4. 접속
- Frontend: http://localhost:5173
- Admin: http://localhost:5173/admin (좌측에 ADMIN_API_TOKEN 입력)
- Backend health: http://localhost:8181/api/health/

### 5. 검증
- 메인 대시보드에서 "🏷️ 업종별" 카드 5개 (법률/병원/의류/숙박/식당) 보이면 OK
- 외부 API 키 비워뒀어도 mock 데이터로 콘텐츠 표시
- Admin > Industries 진입 시 5개 업종 보임

---

## B. 홈서버 LAN (Docker + IP 접근)

홈서버 한 대에서 backend + frontend 모두 돌리고, 사내 PC는 LAN IP로 접근.

### 1. 사전 준비
- 홈서버: Linux (Ubuntu/Debian 권장) + Docker + Compose v2 + Node 20+
- 홈서버의 LAN IP 확인 (예: `192.168.0.50`) — `ip addr` 또는 `ifconfig`
- LAN의 다른 PC가 홈서버 5173, 8181 포트 접근 가능 (방화벽 확인)

### 2. Repo clone
```bash
ssh user@192.168.0.50      # 홈서버 진입
git clone https://github.com/ninewinit01/04.MarketingPulse-260502.git marketing-pulse
cd marketing-pulse
```

### 3. Backend `.env`
```
DJANGO_ALLOWED_HOSTS=192.168.0.50,localhost
CORS_ALLOWED_ORIGINS=http://192.168.0.50:5173
# 나머지는 옵션 A 와 동일
```

```bash
cd backend
make init
```

### 4. Frontend `.env`
```
VITE_API_BASE_URL=http://192.168.0.50:8181/api
```

### 5. Frontend 빌드 + 정적 서빙
LAN에 항상 떠있으려면 `npm run dev` 보다 정적 빌드 후 가벼운 서버로:

```bash
cd frontend
npm install
npm run build
# dist/ 디렉터리에 정적 파일 생성
```

옵션 1 — `npx serve`:
```bash
npx serve -s dist -l 5173
```

옵션 2 — Docker로 nginx serving (영구):
```bash
# frontend/Dockerfile.static (직접 작성)
echo 'FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY <(echo "server { listen 5173; root /usr/share/nginx/html; index index.html; location / { try_files \$uri /index.html; } }") /etc/nginx/conf.d/default.conf' > Dockerfile.static
docker build -f Dockerfile.static -t mp-frontend .
docker run -d -p 5173:5173 --restart unless-stopped --name mp-frontend mp-frontend
```

> 정적 빌드는 Vite가 빌드 시점에 `VITE_API_BASE_URL`을 코드에 박음. URL 변경 시 다시 `npm run build`.

### 6. LAN 다른 PC에서 접속
- http://192.168.0.50:5173 (대시보드)
- http://192.168.0.50:5173/admin

### 7. 자동 수집 (cron) — 옵션 A/B/C 공통
```bash
sudo timedatectl set-timezone Asia/Seoul
chmod +x /path/to/marketing-pulse/backend/scripts/cron.sh
( crontab -l 2>/dev/null; echo "0 8 * * * /path/to/marketing-pulse/backend/scripts/cron.sh" ) | crontab -
```
- 매일 KST 08:00 자동 수집
- 로그: `backend/logs/collect.log` (스크립트가 자동 생성)
- 수동 테스트: `backend/scripts/cron.sh && tail backend/logs/collect.log`

### 8. 자주 나오는 에러 (B)
| 증상 | 해결 |
|------|------|
| LAN 다른 PC에서 5173/8181 안 열림 | 홈서버 방화벽 (`sudo ufw allow 5173/tcp; sudo ufw allow 8181/tcp`) |
| Frontend가 backend 호출 시 CORS 차단 | `backend/.env` `CORS_ALLOWED_ORIGINS` 에 LAN URL 추가 후 `docker compose up -d --force-recreate backend` |
| `DisallowedHost: Invalid HTTP_HOST` | `DJANGO_ALLOWED_HOSTS` 에 LAN IP 추가 후 backend recreate |

---

## C. 도메인 + HTTPS (정식 운영)

홈서버 또는 어디서든 외부 인터넷에서 접근 가능한 정식 배포. Caddy가 Let's Encrypt 인증서 자동 발급.

### 1. 사전 준비
- 본인 소유 도메인 (예: `your-domain.com`)
- 도메인 DNS A 레코드를 서버 공인 IP로 설정 가능
- 라우터 포트포워딩: 외부 80, 443 → 서버 80, 443
- Linux 서버 + Docker + Compose v2
- frontend는 별도 호스팅 (Vercel 추천 — 무료, 자동 빌드)

### 2. DNS 레코드 설정
도메인 DNS 관리 페이지(가비아/Cloudflare/Vercel 등)에서:
- `api.your-domain.com` → A 레코드 → 서버 공인 IP

확인:
```bash
dig +short api.your-domain.com
# 서버 공인 IP가 출력되면 OK (전파 1-10분)
```

### 3. 라우터 포트포워딩
- 외부 80 → 서버 LAN IP : 80
- 외부 443 → 서버 LAN IP : 443

(공유기 관리 페이지 → 포트포워딩)

확인:
```bash
# 다른 네트워크에서 (모바일 데이터 등)
curl -I http://api.your-domain.com  # → 200 또는 308
```

### 4. Caddyfile 도메인 변경
```bash
cd /path/to/marketing-pulse/backend
nano Caddyfile
# api.your-domain.com 부분을 실제 도메인으로
```

### 5. Backend `.env` (production)
```bash
cp .env.example .env
nano .env
```

```
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.your-domain.com
CSRF_TRUSTED_ORIGINS=https://api.your-domain.com
CORS_ALLOWED_ORIGINS=https://app.your-domain.com,https://your-frontend.vercel.app
ADMIN_API_TOKEN=<openssl rand -hex 32>
DJANGO_SECRET_KEY=<openssl rand -base64 50>
DB_NAME=marketing_pulse
DB_USER=mp_user
DB_PASSWORD=<강한 값>
DB_ROOT_PASSWORD=<강한 값>
NAVER_CLIENT_ID=...
NAVER_CLIENT_SECRET=...
YOUTUBE_API_KEY=...
TIME_ZONE=Asia/Seoul
```

### 6. Production 컨테이너 기동
```bash
make prod-init
# = docker compose -f docker-compose.prod.yml up -d --build
#   + makemigrations + migrate + collectstatic + seed + 첫 수집
```

Caddy가 자동으로 ACME challenge 시도 → DNS가 서버 IP를 가리키면 인증서 발급 성공.

확인:
```bash
make prod-logs-caddy   # "certificate obtained successfully" 보이면 OK
curl https://api.your-domain.com/api/health/
# → {"status":"ok","db":true}
```

### 7. Cron 등록 (위 옵션 B의 7번과 동일)

### 8. Frontend 배포 — Vercel (추천)

1. https://vercel.com → "Add New" → "Project"
2. GitHub repo (`ninewinit01/04.MarketingPulse-260502`) import
3. **Root Directory**: `frontend` (모노레포라 명시)
4. Framework: Vite (자동 감지)
5. Build Command: `npm run build`
6. Output Directory: `dist`
7. **Environment Variables**:
   - `VITE_API_BASE_URL` = `https://api.your-domain.com/api`
8. Deploy

배포 후 Vercel 도메인 (예: `marketing-pulse.vercel.app` 또는 커스텀 `app.your-domain.com`)을 backend `.env` 의 `CORS_ALLOWED_ORIGINS`에 추가:

```bash
nano backend/.env
# CORS_ALLOWED_ORIGINS=https://app.your-domain.com,https://marketing-pulse.vercel.app
docker compose -f docker-compose.prod.yml up -d --force-recreate backend
```

### 9. Frontend 자체 호스팅 옵션 (Vercel 안 쓰는 경우)
홈서버에서 직접 정적 호스팅:
- 옵션 B의 5번처럼 nginx 컨테이너로 dist 서빙
- Caddyfile에 frontend block 추가:
  ```
  app.your-domain.com {
      root * /srv/frontend-dist
      try_files {path} /index.html
      file_server
  }
  ```
- DNS에 `app.your-domain.com` A 레코드 추가

### 10. 자주 나오는 에러 (C)
| 증상 | 해결 |
|------|------|
| Caddy 인증서 발급 실패 (`tls-alpn-01` / `http-01` failed) | DNS가 아직 안 가리킴 또는 라우터 포트포워딩 미설정. `dig api.your-domain.com` 확인 후 `make prod-restart` |
| 외부에서 80/443 접근 안 됨 | 라우터 포트포워딩, ISP의 80/443 차단 (한국 일부 ISP), 서버 방화벽 확인 |
| `DisallowedHost` | `DJANGO_ALLOWED_HOSTS` 에 도메인 추가 + force-recreate |
| CORS 차단 | `CORS_ALLOWED_ORIGINS` 에 frontend 도메인 정확히 추가 (https://, 끝 슬래시 없이) |
| `restart` 후 env 안 바뀜 | `restart` 대신 `up -d --force-recreate backend` |

---

## 운영 팁

### DB 백업
```bash
docker run --rm \
    -v marketing-trends-prod_db_data:/data \
    -v $(pwd):/backup alpine \
    tar czf /backup/mp-db-$(date +%F).tgz /data
```

### DB 복원
```bash
docker compose -f docker-compose.prod.yml down
docker volume rm marketing-trends-prod_db_data
docker volume create marketing-trends-prod_db_data
docker run --rm \
    -v marketing-trends-prod_db_data:/data \
    -v $(pwd):/backup alpine \
    tar xzf /backup/mp-db-2026-04-28.tgz -C /
docker compose -f docker-compose.prod.yml up -d
```

### 코드 업데이트
```bash
cd /path/to/marketing-pulse
git pull
cd backend
docker compose -f docker-compose.prod.yml up -d --build backend
# 모델 변경 있으면:
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### 로그 확인
```bash
cd backend
make prod-logs              # 전체
make prod-logs-backend      # backend
make prod-logs-caddy        # 인증서 발급/갱신
tail -f logs/collect.log    # 매일 자동 수집 결과
```

---

## 비용 (참고)

| 항목 | 옵션 A | 옵션 B | 옵션 C (자체 호스팅) | 옵션 C (클라우드) |
|------|-------|-------|---------------------|--------------------|
| 호스팅 | $0 | $0 (전기료) | $0 (전기료) | VM ~$15-30/월 |
| 도메인 | — | — | $10-20/년 | $10-20/년 |
| HTTPS | — | — | $0 (Let's Encrypt) | $0 |
| API 키 | $0 (무료 한도) | $0 | $0 | $0 |
| **합계 (월)** | **$0** | **$0** | **~$1** | **~$15-30** |

(Vercel Hobby 플랜 frontend 무료. NewsAPI/Claude API 추가 시 별도)
