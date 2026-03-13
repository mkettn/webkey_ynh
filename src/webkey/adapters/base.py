from __future__ import annotations

from abc import ABC, abstractmethod
from flask import Request


class IdentityAdapter(ABC):
    @abstractmethod
    def current_user(self, request: Request) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def owned_emails(self, username: str) -> list[str]:
        raise NotImplementedError
