from webkey.app import create_app


def test_me_endpoint_with_static_adapter(monkeypatch) -> None:
    monkeypatch.setenv("WEBKEY_IDENTITY_BACKEND", "static")
    monkeypatch.setenv(
        "WEBKEY_STATIC_USERS_JSON",
        '{"alice":["alice@example.com","alice@other.org"]}',
    )
    app = create_app()
    client = app.test_client()

    response = client.get("/api/me", headers={"X-WebKey-User": "alice"})
    assert response.status_code == 200
    assert response.json["username"] == "alice"
    assert response.json["owned_emails"] == ["alice@example.com", "alice@other.org"]


def test_eligibility_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("WEBKEY_IDENTITY_BACKEND", "static")
    monkeypatch.setenv("WEBKEY_APP_DOMAIN", "example.com")
    monkeypatch.setenv(
        "WEBKEY_STATIC_USERS_JSON",
        '{"alice":["alice@example.com","alice@other.org"]}',
    )
    app = create_app()
    client = app.test_client()
    response = client.post(
        "/api/eligibility",
        headers={"X-WebKey-User": "alice"},
        json={"key_uid_emails": ["alice@example.com", "x@y.z"]},
    )
    assert response.status_code == 200
    assert response.json["eligible_emails"] == ["alice@example.com"]


def test_me_requires_email_addresses(monkeypatch) -> None:
    monkeypatch.setenv("WEBKEY_IDENTITY_BACKEND", "static")
    monkeypatch.setenv("WEBKEY_STATIC_USERS_JSON", '{"alice":[]}')
    app = create_app()
    client = app.test_client()

    response = client.get("/api/me", headers={"X-WebKey-User": "alice"})
    assert response.status_code == 403
    assert response.json["error"] == "no_managed_email"
