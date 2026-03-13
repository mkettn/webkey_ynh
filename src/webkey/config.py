from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_domain: str
    identity_backend: str
    static_users_json: str
    data_dir: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_domain=os.getenv("WEBKEY_APP_DOMAIN", "example.com").strip().lower(),
            identity_backend=os.getenv("WEBKEY_IDENTITY_BACKEND", "static")
            .strip()
            .lower(),
            static_users_json=os.getenv("WEBKEY_STATIC_USERS_JSON", "{}"),
            data_dir=os.getenv("WEBKEY_DATA_DIR", "/tmp/webkey-data").strip(),
        )

    def static_users(self) -> dict[str, list[str]]:
        data = json.loads(self.static_users_json)
        if not isinstance(data, dict):
            raise ValueError("WEBKEY_STATIC_USERS_JSON must be a JSON object")
        normalized: dict[str, list[str]] = {}
        for user, emails in data.items():
            if not isinstance(user, str) or not isinstance(emails, list):
                raise ValueError("Invalid static users mapping")
            normalized[user] = [str(email).strip().lower() for email in emails]
        return normalized
