from datetime import datetime, UTC
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Index, SQLModel, Relationship, UniqueConstraint

__all__ = [
    "BaseFriendship",
    "Friendship",
    "FriendshipStatus",
    "FriendshipApplySource",
]
if TYPE_CHECKING:
    from auth.user import User


class FriendshipStatus(str, Enum):
    pending = "pending"  # 申请中，未处理
    accepted = "accepted"  # 已成为好友
    rejected = "rejected"  # 已拒绝


class FriendshipApplySource(str, Enum):
    search = "search"  # 查找
    email = "email"  # 邮箱
    other = "other"


class BaseFriendship(SQLModel):
    # 状态
    status: FriendshipStatus = Field(default=FriendshipStatus.pending)


class Friendship(BaseFriendship, table=True):
    __tablename__ = "friendship"
    __table_args__ = (
        UniqueConstraint(
            "pair_low_id",
            "pair_high_id",
            name="uq_friendship_pair_low_high",
        ),
        Index(
            "ix_friendship_addressee_status_created_at",
            "addressee_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_friendship_requester_status_created_at",
            "requester_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_friendship_status_requester_created_at",
            "status",
            "requester_id",
            "created_at",
        ),
        Index(
            "ix_friendship_status_addressee_created_at",
            "status",
            "addressee_id",
            "created_at",
        ),
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    accepted_at: datetime | None = Field(default=None)
    # 申请者
    requester_id: UUID = Field(foreign_key="user.id", primary_key=True)
    # 接受者
    addressee_id: UUID = Field(foreign_key="user.id", primary_key=True)
    # 无向关系唯一键：按 UUID 排序后存储
    pair_low_id: UUID = Field(foreign_key="user.id", nullable=False)
    pair_high_id: UUID = Field(foreign_key="user.id", nullable=False)
    # 申请消息
    request_message: str | None = Field(default=None)
    # 查找来源
    source: FriendshipApplySource = Field(default=FriendshipApplySource.search)
    # 关系：这条好友记录的发起人
    requester: "User" = Relationship(
        back_populates="sent_friendships",
        sa_relationship_kwargs={
            "foreign_keys": "Friendship.requester_id",
            "lazy": "selectin",
        },
    )

    # 关系：这条好友记录的接收人
    addressee: "User" = Relationship(
        back_populates="received_friendships",
        sa_relationship_kwargs={
            "foreign_keys": "Friendship.addressee_id",
            "lazy": "selectin",
        },
    )
