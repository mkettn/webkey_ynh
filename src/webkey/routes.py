from __future__ import annotations

from flask import Flask, Response, jsonify, request, send_file

from .adapters.base import IdentityAdapter
from .config import Settings
from .core import eligible_emails
from .core.wkd_paths import hu_path, policy_path


def register_routes(app: Flask) -> None:
    def _user_with_emails() -> tuple[str | None, list[str], tuple[object, int] | None]:
        adapter: IdentityAdapter = app.config["webkey.identity_adapter"]
        username = adapter.current_user(request)
        if not username:
            return None, [], (jsonify({"error": "unauthenticated"}), 401)

        owned = adapter.owned_emails(username)
        if not owned:
            return (
                username,
                [],
                (
                    jsonify(
                        {
                            "error": "no_managed_email",
                            "message": "No email address found for this account",
                        }
                    ),
                    403,
                ),
            )
        return username, owned, None

    @app.get("/")
    def index() -> tuple[object, int]:
        username, owned, error = _user_with_emails()
        if error:
            return error
        return (
            jsonify(
                {
                    "service": "webkey",
                    "message": "WKD UI/API scaffold",
                    "username": username,
                    "owned_emails": owned,
                }
            ),
            200,
        )

    @app.get("/.well-known/openpgpkey/<domain>/policy")
    def wkd_policy(domain: str) -> Response:
        settings: Settings = app.config["webkey.settings"]
        if domain != settings.app_domain:
            return Response(status=404)

        path = policy_path(settings.data_dir, domain)
        if not path.exists():
            return Response("", mimetype="text/plain")
        return send_file(path, mimetype="text/plain")

    @app.get("/.well-known/openpgpkey/<domain>/hu/<key_hash>")
    def wkd_key(domain: str, key_hash: str) -> Response:
        settings: Settings = app.config["webkey.settings"]
        if domain != settings.app_domain:
            return Response(status=404)

        path = hu_path(settings.data_dir, domain, key_hash)
        if not path.exists() or not path.is_file():
            return Response(status=404)
        return send_file(path, mimetype="application/octet-stream")

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.get("/api/me")
    def me() -> tuple[object, int]:
        username, owned, error = _user_with_emails()
        if error:
            return error

        return jsonify(
            {
                "username": username,
                "owned_emails": owned,
            }
        ), 200

    @app.post("/api/eligibility")
    def eligibility() -> tuple[object, int]:
        settings: Settings = app.config["webkey.settings"]
        username, owned, error = _user_with_emails()
        if error:
            return error

        body = request.get_json(silent=True) or {}
        key_uid_emails = body.get("key_uid_emails")
        if not isinstance(key_uid_emails, list):
            return jsonify({"error": "key_uid_emails must be a list"}), 400

        eligible = eligible_emails(
            owned_emails=owned,
            key_uid_emails=[str(email) for email in key_uid_emails],
            domain=settings.app_domain,
        )
        return jsonify(
            {
                "username": username,
                "domain": settings.app_domain,
                "owned_emails": owned,
                "eligible_emails": eligible,
            }
        ), 200
