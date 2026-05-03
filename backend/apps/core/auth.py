"""ADMIN_API_TOKEN 단일 토큰 인증.

Authorization: Bearer <ADMIN_API_TOKEN> 헤더가 있으면 익명 인증된 사용자로 통과.
admin/* 엔드포인트는 IsAdminToken 권한과 함께 사용.
"""
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions, permissions


class _AdminUser(AnonymousUser):
    """익명 객체이지만 admin 권한 통과용. is_authenticated만 True."""

    @property
    def is_authenticated(self):
        return True

    @property
    def is_staff(self):
        return True


class AdminTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()
        if not header or header[0].lower() != self.keyword.lower().encode():
            return None
        if len(header) != 2:
            raise exceptions.AuthenticationFailed("Invalid Authorization header")
        try:
            token = header[1].decode()
        except UnicodeError as exc:
            raise exceptions.AuthenticationFailed("Invalid token encoding") from exc

        expected = settings.ADMIN_API_TOKEN
        if not expected or token != expected:
            raise exceptions.AuthenticationFailed("Invalid admin token")
        return (_AdminUser(), token)

    def authenticate_header(self, request):
        return self.keyword


class IsAdminToken(permissions.BasePermission):
    """admin endpoint에서만 사용. AdminTokenAuthentication 통과 여부 확인."""

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, "is_staff", False))
