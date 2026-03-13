from .base import IdentityAdapter
from .static_identity import StaticIdentityAdapter
from .yunohost_identity import YunoHostIdentityAdapter

__all__ = [
    "IdentityAdapter",
    "StaticIdentityAdapter",
    "YunoHostIdentityAdapter",
]
