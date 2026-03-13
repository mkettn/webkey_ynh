from __future__ import annotations

import json
import subprocess
from flask import Request

from .base import IdentityAdapter


class YunoHostIdentityAdapter(IdentityAdapter):
    def current_user(self, request: Request) -> str | None:
        username = request.headers.get("YNH_USER", "").strip()
        return username or None

    def owned_emails(self, username: str) -> list[str]:
        raw = subprocess.check_output(
            ["yunohost", "user", "info", username, "--output-as", "json"],
            text=True,
        )
        data = json.loads(raw)
        user = data.get("user", {})
        emails = []

        primary = user.get("mail")
        if isinstance(primary, str) and primary:
            emails.append(primary.lower())

        aliases = user.get("mail-aliases") or user.get("mail_aliases") or []
        if isinstance(aliases, list):
            emails.extend(str(alias).strip().lower() for alias in aliases if alias)

        deduped = sorted(set(emails))
        return deduped
