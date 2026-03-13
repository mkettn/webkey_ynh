from __future__ import annotations

from .email_utils import email_domain, normalize_email


def eligible_emails(
    *,
    owned_emails: list[str],
    key_uid_emails: list[str],
    domain: str,
) -> list[str]:
    target_domain = domain.strip().lower()
    owned = {normalize_email(email) for email in owned_emails}
    key_uids = {normalize_email(email) for email in key_uid_emails}

    eligible = []
    for email in sorted(owned & key_uids):
        if email_domain(email) == target_domain:
            eligible.append(email)
    return eligible
