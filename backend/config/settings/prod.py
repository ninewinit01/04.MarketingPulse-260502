"""Production settings — VM + Caddy reverse proxy + Let's Encrypt."""
import os

from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE

DEBUG = False

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "api.joosung.dev").split(",")
    if h.strip()
]

# Caddy(443) → backend(8000) — proxy 헤더로 https 인식
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False  # Caddy가 80→443 처리
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    "https://api.joosung.dev",
    *[
        o.strip()
        for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
        if o.strip()
    ],
]

# CORS — env에서 받은 frontend origin들만 허용
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
CORS_ALLOW_ALL_ORIGINS = False

# Static files — whitenoise (Django Admin 정적 파일 서빙용)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE = [
    MIDDLEWARE[0],  # corsheaders
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[2:],  # security 다음 (sessions ~ clickjacking)
]

# 프록시 뒤에 있으니 Logging은 stdout으로 (docker logs)
