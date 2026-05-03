.DEFAULT_GOAL := help
SHELL := /bin/bash

# Backend(+DB)는 docker로 운영. Frontend는 ../frontend 에서 npm run dev 직접.

# ──────── Setup ────────

.PHONY: help
help: ## 사용 가능한 명령 보기
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: env
env: ## .env 파일 생성 (없을 때만)
	@if [ ! -f .env ]; then cp .env.example .env && echo "✓ .env 생성 완료. 필요시 값 수정하세요."; else echo "ℹ .env 이미 존재."; fi

# ──────── Build & Run ────────

.PHONY: build
build: env ## backend+db 이미지 빌드
	docker compose build

.PHONY: up
up: env ## backend + db 백그라운드 실행
	docker compose up -d

.PHONY: up-build
up-build: env ## 빌드 + 실행
	docker compose up -d --build

.PHONY: down
down: ## 컨테이너 중지/제거 (볼륨 유지)
	docker compose down

.PHONY: nuke
nuke: ## 컨테이너 + 볼륨 전부 제거 (DB 초기화)
	docker compose down -v

.PHONY: restart
restart: ## backend 재시작 (env 다시 로드)
	docker compose restart backend

# ──────── DB / 데이터 ────────

.PHONY: migrate
migrate: ## DB 마이그레이션
	docker compose exec backend python manage.py migrate

.PHONY: makemigrations
makemigrations: ## 마이그레이션 파일 생성
	docker compose exec backend python manage.py makemigrations industries content classifier collectors dashboard llm core

.PHONY: seed
seed: ## 시드 데이터 (업종 5종 + 키워드 + 소스 4종)
	docker compose exec backend python manage.py seed_data

.PHONY: collect
collect: ## 수집 1회 실행 (mock 또는 실제 API)
	docker compose exec backend python manage.py run_collection

.PHONY: superuser
superuser: ## Django Admin용 superuser 생성
	docker compose exec backend python manage.py createsuperuser

.PHONY: shell
shell: ## Django shell
	docker compose exec backend python manage.py shell

.PHONY: dbshell
dbshell: ## MariaDB CLI 접속
	docker compose exec db mariadb -u$$(grep ^DB_USER .env | cut -d= -f2) -p$$(grep ^DB_PASSWORD .env | cut -d= -f2) $$(grep ^DB_NAME .env | cut -d= -f2)

# ──────── 통합 ────────

.PHONY: init
init: up-build ## 처음 시작: build + up + makemigrations + migrate + seed + collect
	@echo "→ DB가 healthy 될 때까지 대기..."
	@sleep 8
	@$(MAKE) makemigrations
	@$(MAKE) migrate
	@$(MAKE) seed
	@$(MAKE) collect
	@echo ""
	@echo "✓ 초기화 완료!"
	@echo ""
	@echo "  Backend:   http://localhost:8181/api/health/"
	@echo "  Frontend:  새 터미널에서 → cd ../frontend && npm install && npm run dev"
	@echo "  토큰:      .env의 ADMIN_API_TOKEN 값을 /admin 페이지에 입력"

.PHONY: reset
reset: nuke init ## 전체 초기화 + 재구축 (위험)

# ──────── 로그 / 상태 ────────

.PHONY: logs
logs: ## 전체 로그 follow
	docker compose logs -f

.PHONY: logs-backend
logs-backend: ## backend 로그
	docker compose logs -f backend

.PHONY: logs-db
logs-db: ## db 로그
	docker compose logs -f db

.PHONY: ps
ps: ## 컨테이너 상태
	docker compose ps

.PHONY: health
health: ## health check
	@curl -sS http://localhost:8181/api/health/ | python3 -m json.tool || echo "백엔드 응답 없음"

# ──────── 개발 ────────

.PHONY: bash
bash: ## backend 컨테이너 셸
	docker compose exec backend bash

# ──────── Production (docker-compose.prod.yml + Caddy) ────────

PROD := docker compose -f docker-compose.prod.yml

.PHONY: prod-up
prod-up: ## prod 빌드 + 실행 (gunicorn + caddy + db)
	$(PROD) up -d --build

.PHONY: prod-down
prod-down: ## prod 중지
	$(PROD) down

.PHONY: prod-logs
prod-logs: ## prod 전체 로그 follow
	$(PROD) logs -f

.PHONY: prod-logs-backend
prod-logs-backend: ## prod backend 로그
	$(PROD) logs -f backend

.PHONY: prod-logs-caddy
prod-logs-caddy: ## prod caddy 로그 (인증서 발급/갱신 디버깅)
	$(PROD) logs -f caddy

.PHONY: prod-migrate
prod-migrate: ## prod DB 마이그레이션
	$(PROD) exec backend python manage.py makemigrations industries content classifier collectors dashboard llm core
	$(PROD) exec backend python manage.py migrate

.PHONY: prod-collectstatic
prod-collectstatic: ## prod 정적 파일 수집 (whitenoise용)
	$(PROD) exec backend python manage.py collectstatic --noinput

.PHONY: prod-seed
prod-seed: ## prod 시드
	$(PROD) exec backend python manage.py seed_data

.PHONY: prod-collect
prod-collect: ## prod 수집 1회
	$(PROD) exec backend python manage.py run_collection

.PHONY: prod-init
prod-init: prod-up ## prod 첫 실행: up + migrate + collectstatic + seed + collect
	@sleep 15
	@$(MAKE) prod-migrate
	@$(MAKE) prod-collectstatic
	@$(MAKE) prod-seed
	@$(MAKE) prod-collect

.PHONY: prod-restart
prod-restart: ## prod backend + caddy 재시작 (.env 변경 후)
	$(PROD) restart backend caddy

.PHONY: test-api
test-api: ## API 동작 확인 (health + 공개/admin 엔드포인트)
	@echo "→ /api/health/"
	@curl -sS http://localhost:8181/api/health/ | python3 -m json.tool
	@echo ""
	@echo "→ /api/industries/ (public)"
	@curl -sS http://localhost:8181/api/industries/ | python3 -m json.tool | head -30
	@echo ""
	@echo "→ /api/admin/industries/ (token 필요)"
	@curl -sS -H "Authorization: Bearer $$(grep ^ADMIN_API_TOKEN .env | cut -d= -f2)" http://localhost:8181/api/admin/industries/ | python3 -m json.tool | head -30
