from pathlib import Path

from webkey.app import create_app


def test_wkd_policy_and_key_routes(monkeypatch, tmp_path: Path) -> None:
    domain = "example.com"
    policy = tmp_path / ".well-known" / "openpgpkey" / domain / "policy"
    key = tmp_path / ".well-known" / "openpgpkey" / domain / "hu" / "abc123"
    key.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text("", encoding="utf-8")
    key.write_bytes(b"public-key-binary")

    monkeypatch.setenv("WEBKEY_APP_DOMAIN", domain)
    monkeypatch.setenv("WEBKEY_IDENTITY_BACKEND", "static")
    monkeypatch.setenv("WEBKEY_STATIC_USERS_JSON", "{}")
    monkeypatch.setenv("WEBKEY_DATA_DIR", str(tmp_path))

    app = create_app()
    client = app.test_client()

    policy_response = client.get(f"/.well-known/openpgpkey/{domain}/policy")
    assert policy_response.status_code == 200

    key_response = client.get(f"/.well-known/openpgpkey/{domain}/hu/abc123")
    assert key_response.status_code == 200
    assert key_response.data == b"public-key-binary"
