from __future__ import annotations

from flask import Flask

from .adapters import StaticIdentityAdapter, YunoHostIdentityAdapter
from .adapters.base import IdentityAdapter
from .config import Settings
from .routes import register_routes


def _build_adapter(settings: Settings) -> IdentityAdapter:
    if settings.identity_backend == "yunohost":
        return YunoHostIdentityAdapter()
    if settings.identity_backend == "static":
        return StaticIdentityAdapter(settings.static_users())
    raise ValueError(f"Unknown WEBKEY_IDENTITY_BACKEND: {settings.identity_backend}")


def create_app() -> Flask:
    app = Flask(__name__)
    settings = Settings.from_env()
    adapter = _build_adapter(settings)
    app.config["webkey.settings"] = settings
    app.config["webkey.identity_adapter"] = adapter
    register_routes(app)
    return app
