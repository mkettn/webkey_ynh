# Web Key Directory, packaged for YunoHost

Self-hosted OpenPGP Web Key Directory (WKD) service with a user-facing key management API/UI.

This repository contains both:
- the generic WKD application code (can run without YunoHost), and
- the YunoHost packaging/integration layer (manifest, scripts, nginx/systemd templates).

## What this app does

- Lets authenticated users manage one public key per account.
- Publishes eligible user IDs through WKD under `/.well-known/openpgpkey/...`.
- Restricts publication to email addresses owned by the logged-in account.
- Supports YunoHost multi-instance (one WKD domain context per instance).

## Current design choices

- Advanced WKD deployment model with domains like `openpgpkey.example.com`.
- UI/API is authenticated; WKD lookup endpoints are public.
- One key per account per instance; extra key UIDs are allowed but ignored unless eligible.
- YunoHost-specific identity resolution is implemented as an adapter, not in core logic.

For full rationale and decisions, see `DESIGN.md`.

## Repository layout

- `src/webkey/`: application source code
- `manifest.toml`: YunoHost package manifest
- `scripts/`: YunoHost lifecycle scripts
- `conf/`: nginx/systemd/env templates
- `tests/`: unit and integration tests

## Developer quick start (without YunoHost)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
WEBKEY_IDENTITY_BACKEND=static \
WEBKEY_APP_DOMAIN=example.com \
WEBKEY_STATIC_USERS_JSON='{"alice":["alice@example.com"]}' \
python -c "from webkey.app import create_app; create_app().run()"
```

Use header `X-WebKey-User: alice` for authenticated API calls in static mode.

## YunoHost package testing

- Static checks: `package_linter`
- Integration/lifecycle: `package_check` with `tests.toml`

General packaging docs: <https://doc.yunohost.org/dev/packaging/>

## License

MIT. See `LICENSE`.
