from webkey.core.eligibility import eligible_emails


def test_eligible_emails_intersection_and_domain_filter() -> None:
    result = eligible_emails(
        owned_emails=["alice@example.com", "alice@other.org"],
        key_uid_emails=["alice@example.com", "someone@else.net"],
        domain="example.com",
    )
    assert result == ["alice@example.com"]


def test_eligible_emails_normalizes_case() -> None:
    result = eligible_emails(
        owned_emails=["Alice@Example.COM"],
        key_uid_emails=["alice@example.com"],
        domain="example.com",
    )
    assert result == ["alice@example.com"]
