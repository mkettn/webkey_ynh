# webkey_ynh - Design Decisions

This document captures the design decisions agreed so far for a Web Key Directory (WKD) service packaged for YunoHost, with a user UI for key management.

## Goal

- Build a YunoHost app so users can publish their OpenPGP public keys.
- Published keys must be fetchable from the Internet via WKD.
- Users manage keys themselves through a web UI.

## Product Scope

- One app instance manages one WKD domain context.
- The app supports multiple domains by using YunoHost multi-instance installs.
- This project targets WKD serving and key management (not a general keyserver).

## Coupling Strategy

- The app core must remain YunoHost-agnostic.
- YunoHost-specific behavior must live in packaging and adapter layers.
- The service should be runnable outside YunoHost with a different identity provider.
- YunoHost acts as deployment/integration glue, not as a hard runtime dependency in core logic.

## Architecture Boundary

- Core layer (`src/core/`) contains WKD logic only:
  - key parsing/validation,
  - UID extraction and filtering,
  - WKD hash/path generation,
  - publication and storage workflows.
- Identity adapter layer (`src/adapters/`) provides an interface for:
  - current authenticated user identity,
  - owned email resolution for that user.
- YunoHost adapter implements that interface using SSO headers and YunoHost user data.
- A non-YunoHost adapter (tests/dev) is provided to keep core tests independent.

## YunoHost Deployment Model

- `multi_instance = true`.
- One instance per domain (e.g. one for `openpgpkey.example-a.com`, one for `openpgpkey.example-b.org`).
- No cross-instance data sharing in v1.
- Each instance manages only addresses for its own domain.

## Domain and Routing Model

- Use WKD advanced mode host pattern (`openpgpkey.<mail-domain>`).
- Example expected host: `openpgpkey.example.com`.
- UI and WKD can be served from the same host, but with different access controls.
- WKD endpoints are public under `/.well-known/openpgpkey/...`.
- UI/API endpoints are authenticated via YunoHost SSO.

## Critical Separation of Concerns

- Human management surface (UI/API): authenticated.
- Machine lookup surface (WKD): public, unauthenticated.
- WKD paths must never require login or HTTP auth challenge.
- Authentication/ownership source is pluggable via adapter, not hardcoded into WKD core.

## Ownership and Authorization Rules

- Users may only publish keys for email addresses assigned to their YunoHost account.
- Assigned addresses include primary address and aliases.
- One active key per YunoHost account per app instance.
- A key may contain multiple UID emails.
- Extra UID emails not owned by the user are allowed, but ignored for publishing.

### Identity Provider Note

- In the packaged YunoHost deployment, account ownership is resolved from YunoHost users/aliases.
- In non-YunoHost deployments, ownership can be provided by another adapter implementing the same interface.

## Domain Filtering Rules

- Each instance only publishes identities for that instance's target domain.
- Upload acceptance requires:
  - at least one key UID email owned by the logged-in user, and
  - at least one key UID email matching the instance domain.
- Publish set is computed as:
  - `owned_emails intersect key_uid_emails intersect instance_domain_emails`.

## Key Lifecycle Rules

- Upload creates/replaces the user's single active key for the instance.
- Replace is atomic (old publication removed, new publication generated).
- Delete removes the active key and all WKD files published by that user in this instance.

## WKD Protocol and File Behavior

- Implement WKD-compatible hashing and path generation.
- Serve key material as binary OpenPGP key data.
- Keep `policy` file present.
- Set response headers suitable for WKD clients, including `application/octet-stream`.
- Add CORS header (`Access-Control-Allow-Origin: *`) on WKD responses.

## Security and Validation

- Enforce upload size limits.
- Accept armored or binary public keys.
- Reject secret key material.
- Parse keys in isolated temporary GnuPG context (do not pollute system keyring).
- Use strict normalization/validation for emails and domain matching.
- Use atomic file writes and locking for metadata/publication updates.

## Storage Model (v1)

- Filesystem-backed storage with per-instance metadata.
- Metadata keyed by generic account identifier from the active identity adapter (single key per account in that instance).
- Track fingerprint, key UID list, timestamps, and published WKD hashes.

## App Packaging Direction

- Standard YunoHost package structure (`manifest.toml`, `scripts/`, `conf/`, `src/`, `tests/`).
- Nginx config provides public WKD locations and protected UI/API routes.
- Systemd-managed backend service (planned stack: Python/Flask + gunicorn).
- Install script checks for `/.well-known/openpgpkey` conflicts on chosen domain.
- No subpath-based WKD install model.
- YunoHost package is responsible for wiring the YunoHost identity adapter and runtime env.

## Testing Strategy

- Layer 1: unit tests for WKD hash/path logic and eligibility rules.
- Layer 2: app integration tests for upload/replace/delete behavior.
- Layer 3: protocol checks (public WKD fetch, headers, `gpg --locate-keys`).
- Layer 4: YunoHost packaging tests (`package_linter`, `package_check`, `tests.toml`).

### YunoHost Integration Test Notes

- Use disposable test environments (container/VM-like) via YunoHost tooling.
- Validate install/remove/upgrade/backup/restore lifecycle.
- Add `curl_tests` for:
  - authenticated UI endpoint(s),
  - public WKD policy and key URL behavior.

## Open Questions Deferred

- Direct WKD fallback support is deferred; focus is advanced-mode deployment model.
- Potential future shared-backend mode across instances is out of v1 scope.
