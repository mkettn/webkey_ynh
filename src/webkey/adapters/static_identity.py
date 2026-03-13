from __future__ import annotations

from flask import Request

from .base import IdentityAdapter


class StaticIdentityAdapter(IdentityAdapter):
    def __init__(self, users: dict[str, list[str]]) -> None:
        self._users = users

    def current_user(self, request: Request) -> str | None:
        username = request.headers.get("X-WebKey-User", "").strip()
        if not username:
            return None
        if username not in self._users:
            return None
        return username

    def owned_emails(self, username: str) -> list[str]:
        return list(self._users.get(username, []))
