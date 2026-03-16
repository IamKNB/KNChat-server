import base64
import binascii
import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import or_
from sqlmodel import Session, select, func

from auth.user import User

__all__ = [
    "InvalidCursorError",
    "UserSearchPage",
    "get_user_public_by_id",
    "search_users",
]


class InvalidCursorError(ValueError):
    def __init__(self, cursor: str | None) -> None:
        super().__init__("invalid cursor")
        self.cursor = cursor


@dataclass
class UserSearchPage:
    items: list[User]
    has_more: bool
    next_cursor: str | None


def _encode_cursor_payload(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")


def _decode_cursor_payload(cursor: str | None) -> dict[str, Any] | None:
    if cursor is None:
        return None

    try:
        padded = cursor + ("=" * (-len(cursor) % 4))
        decoded = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        payload = json.loads(decoded)
        if not isinstance(payload, dict):
            raise InvalidCursorError(cursor)
    except (
        ValueError,
        TypeError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        binascii.Error,
    ):
        raise InvalidCursorError(cursor)

    return payload


def _encode_cursor(user_id: UUID) -> str:
    return _encode_cursor_payload({"id": str(user_id)})


def _decode_cursor(cursor: str | None) -> UUID | None:
    payload = _decode_cursor_payload(cursor)
    if payload is None:
        return None
    try:
        raw_id = payload["id"]
        return UUID(raw_id)
    except (KeyError, TypeError, ValueError):
        raise InvalidCursorError(cursor)


def search_users(
    session: Session,
    *,
    email: str | None,
    username: str | None,
    cursor: str | None,
    limit: int,
) -> UserSearchPage:
    email_filter = email.strip().lower() if email else None
    username_filter = username.strip().lower() if username else None

    statement = select(User).order_by(User.id)
    filters = []
    if email_filter:
        filters.append(func.lower(User.email) == email_filter)
    if username_filter:
        filters.append(func.lower(User.username).like(f"%{username_filter}%"))
    if filters:
        if len(filters) == 1:
            statement = statement.where(filters[0])
        else:
            statement = statement.where(or_(*filters))

    anchor_id = _decode_cursor(cursor)
    if anchor_id is not None:
        statement = statement.where(User.id > anchor_id)

    rows = list(session.exec(statement.limit(limit + 1)))
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor = _encode_cursor(items[-1].id) if has_more and items else None

    return UserSearchPage(items=items, has_more=has_more, next_cursor=next_cursor)


def get_user_public_by_id(session: Session, user_id: UUID) -> User | None:
    return session.get(User, user_id)
