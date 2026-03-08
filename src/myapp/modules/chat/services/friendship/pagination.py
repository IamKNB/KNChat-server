import base64
import binascii
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlmodel import func

from myapp.modules.chat.schemas import Friendship

from .errors import raise_friendship_service_error
from .types import FriendshipListMode, MAX_PAGE_LIMIT

__all__ = [
    "KeysetAnchor",
    "build_keyset_filter",
    "decode_cursor",
    "encode_cursor",
    "sort_time_expr",
    "sort_time_of",
    "validate_limit",
]


@dataclass
class KeysetAnchor:
    sort_time: datetime
    pair_low_id: UUID
    pair_high_id: UUID


def encode_cursor(anchor: KeysetAnchor) -> str:
    payload = {
        "sort_time": anchor.sort_time.isoformat(),
        "pair_low_id": str(anchor.pair_low_id),
        "pair_high_id": str(anchor.pair_high_id),
    }
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")


def decode_cursor(cursor: str | None) -> KeysetAnchor | None:
    if cursor is None:
        return None

    try:
        padded = cursor + ("=" * (-len(cursor) % 4))
        decoded = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        payload = json.loads(decoded)
        sort_time = datetime.fromisoformat(payload["sort_time"])
        pair_low_id = UUID(payload["pair_low_id"])
        pair_high_id = UUID(payload["pair_high_id"])
    except (
            ValueError,
            TypeError,
            KeyError,
            json.JSONDecodeError,
            UnicodeDecodeError,
            binascii.Error,
    ):
        raise_friendship_service_error(
            status_code=400,
            code="invalid_cursor",
            message="invalid cursor",
            detail=cursor,
        )
        raise RuntimeError("unreachable")

    return KeysetAnchor(
        sort_time=sort_time,
        pair_low_id=pair_low_id,
        pair_high_id=pair_high_id,
    )


def validate_limit(limit: int) -> None:
    if limit < 1 or limit > MAX_PAGE_LIMIT:
        raise_friendship_service_error(
            status_code=400,
            code="invalid_limit",
            message="invalid pagination parameters",
            detail=f"limit must be between 1 and {MAX_PAGE_LIMIT}",
        )


def sort_time_expr(mode: FriendshipListMode):
    if mode == FriendshipListMode.accepted:
        return func.coalesce(Friendship.accepted_at, Friendship.created_at)
    return Friendship.created_at


def sort_time_of(item: Friendship, mode: FriendshipListMode) -> datetime:
    if mode == FriendshipListMode.accepted:
        return item.accepted_at or item.created_at
    return item.created_at


def build_keyset_filter(*, current_sort_expr, anchor: KeysetAnchor):
    return (
            (current_sort_expr < anchor.sort_time)
            | ((current_sort_expr == anchor.sort_time) & (Friendship.pair_low_id < anchor.pair_low_id))
            | (
                    (current_sort_expr == anchor.sort_time)
                    & (Friendship.pair_low_id == anchor.pair_low_id)
                    & (Friendship.pair_high_id < anchor.pair_high_id)
            )
    )
