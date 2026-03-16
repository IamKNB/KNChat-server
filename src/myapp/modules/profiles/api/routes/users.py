from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth import get_user
from auth.user import User, User2Public
from db import SessionDep
from myapp.common.api import CursorMeta, PaginationParams
from myapp.modules.profiles.schemas import UserPublicListEnvelope
from myapp.modules.profiles.services import (
    InvalidCursorError,
    get_user_public_by_id,
    search_users,
)

__all__ = [
    "router",
]

router = APIRouter(prefix="/users")


@router.get("/search", response_model=UserPublicListEnvelope)
def search_users_route(
    session: SessionDep,
    pagination: PaginationParams = Depends(),
    email: str | None = Query(default=None),
    username: str | None = Query(default=None),
    current_user: User = Depends(get_user),
) -> UserPublicListEnvelope:
    email_value = email.strip() if email else None
    username_value = username.strip() if username else None

    if not email_value and not username_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="email or username is required",
        )

    try:
        page = search_users(
            session,
            email=email_value,
            username=username_value,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )
    except InvalidCursorError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UserPublicListEnvelope(
        code="users_listed",
        message="users listed",
        data=[User2Public.model_validate(item) for item in page.items],
        meta=CursorMeta(has_more=page.has_more, next_cursor=page.next_cursor),
    )


@router.get("/{user_id}", response_model=User2Public)
def get_user_public(
    user_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_user),
) -> User2Public:
    user = get_user_public_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )
    return User2Public.model_validate(user)
