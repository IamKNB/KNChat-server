from dataclasses import dataclass
from enum import Enum

from myapp.modules.chat.schemas import Friendship

__all__ = [
    "DEFAULT_PAGE_LIMIT",
    "MAX_PAGE_LIMIT",
    "FriendshipListMode",
    "FriendshipPage",
]

DEFAULT_PAGE_LIMIT = 20
MAX_PAGE_LIMIT = 100


class FriendshipListMode(str, Enum):
    pending = "pending"
    accepted = "accepted"


@dataclass
class FriendshipPage:
    items: list[Friendship]
    has_more: bool
    next_cursor: str | None
