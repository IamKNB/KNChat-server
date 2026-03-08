from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlmodel import SQLModel

from auth.user import User2Friends, User2Public
from .friendship import FriendshipApplySource, FriendshipStatus

__all__ = [
    "CURSOR_EXAMPLE",
    "CreateFriendshipRequestBody",
    "CursorMeta",
    "ErrorDetail",
    "ErrorEnvelope",
    "FriendshipAcceptedData",
    "FriendshipAcceptedEnvelope",
    "FriendshipAcceptedListEnvelope",
    "FriendshipDirection",
    "FriendshipPendingData",
    "FriendshipPendingEnvelope",
    "FriendshipPendingListEnvelope",
]

ErrorDetail = str | dict[str, Any] | list[dict[str, Any]] | None
CURSOR_EXAMPLE = (
    "eyJzb3J0X3RpbWUiOiIyMDI2LTAzLTA4VDAxOjAwOjAwKzAwOjAwIiwicGFpcl9sb3dfaWQiOiIx"
    "MTExMTExMS0xMTExLTExMTEtMTExMS0xMTExMTExMTExMTEiLCJwYWlyX2hpZ2hfaWQiOiIyMjIy"
    "MjIyMi0yMjIyLTIyMjItMjIyMi0yMjIyMjIyMjIyMjIifQ=="
)


class FriendshipDirection(str, Enum):
    incoming = "incoming"
    outgoing = "outgoing"


class CreateFriendshipRequestBody(SQLModel):
    addressee_id: UUID
    request_message: str | None = None
    source: FriendshipApplySource = FriendshipApplySource.search


class FriendshipPendingData(SQLModel):
    status: FriendshipStatus
    created_at: datetime
    source: FriendshipApplySource
    request_message: str | None = None
    peer: User2Public
    direction: FriendshipDirection


class FriendshipAcceptedData(SQLModel):
    status: FriendshipStatus
    created_at: datetime
    accepted_at: datetime | None
    source: FriendshipApplySource
    request_message: str | None = None
    peer: User2Friends
    direction: FriendshipDirection


class CursorMeta(SQLModel):
    has_more: bool
    next_cursor: str | None = None


class ErrorEnvelope(SQLModel):
    code: str
    message: str
    detail: ErrorDetail = None


class FriendshipPendingEnvelope(SQLModel):
    code: str
    message: str
    data: FriendshipPendingData


class FriendshipAcceptedEnvelope(SQLModel):
    code: str
    message: str
    data: FriendshipAcceptedData


class FriendshipPendingListEnvelope(SQLModel):
    code: str
    message: str
    data: list[FriendshipPendingData]
    meta: CursorMeta


class FriendshipAcceptedListEnvelope(SQLModel):
    code: str
    message: str
    data: list[FriendshipAcceptedData]
    meta: CursorMeta
