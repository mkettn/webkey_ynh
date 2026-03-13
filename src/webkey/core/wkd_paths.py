from __future__ import annotations

from pathlib import Path


def policy_path(data_dir: str, domain: str) -> Path:
    return Path(data_dir) / ".well-known" / "openpgpkey" / domain / "policy"


def hu_path(data_dir: str, domain: str, key_hash: str) -> Path:
    return Path(data_dir) / ".well-known" / "openpgpkey" / domain / "hu" / key_hash
