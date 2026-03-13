from __future__ import annotations


def normalize_email(value: str) -> str:
    return value.strip().lower()


def email_domain(value: str) -> str:
    email = normalize_email(value)
    local, at, domain = email.rpartition("@")
    if not at or not local or not domain:
        raise ValueError(f"Invalid email: {value}")
    return domain
