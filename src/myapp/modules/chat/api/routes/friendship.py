from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from auth import get_user
from auth.user import User
from db import SessionDep
from myapp.modules.chat.api.errors.friendship import FRIENDSHIP_ERROR_RESPONSES, FriendshipRoute
from myapp.modules.chat.schemas.friendship_api import (
    CURSOR_EXAMPLE,
    CreateFriendshipRequestBody,
    FriendshipAcceptedEnvelope,
    FriendshipAcceptedListEnvelope,
    FriendshipDirection,
    FriendshipPendingEnvelope,
    FriendshipPendingListEnvelope,
)
from myapp.modules.chat.services import (
    accept_friendship_request,
    build_accept_friendship_response,
    build_cancel_friendship_response,
    build_create_friendship_response,
    build_list_accepted_friendships_response,
    build_list_friendship_requests_response,
    build_reject_friendship_response,
    build_remove_friendship_response,
    cancel_friendship_request,
    create_friendship_request,
    list_accepted_friendships as list_accepted_friendships_service,
    list_friendship_requests as list_friendship_requests_service,
    reject_friendship_request,
    remove_friendship as remove_friendship_service,
)

__all__ = ["router"]

CURSOR_DESCRIPTION = (
    "Opaque keyset cursor from previous response `meta.next_cursor`. "
    "Clients should pass through next_cursor directly."
)

router = APIRouter(
    prefix="/friendships",
    tags=["friendships"],
    route_class=FriendshipRoute,
    responses=FRIENDSHIP_ERROR_RESPONSES,
)


@router.post("/requests", response_model=FriendshipPendingEnvelope, status_code=status.HTTP_201_CREATED)
def create_friendship(
        body: CreateFriendshipRequestBody,
        session: SessionDep,
        current_user: User = Depends(get_user),
) -> FriendshipPendingEnvelope:
    friendship = create_friendship_request(
        session=session,
        actor=current_user,
        addressee_id=body.addressee_id,
        request_message=body.request_message,
        source=body.source,
    )
    return build_create_friendship_response(friendship, current_user.id)


@router.get("/requests", response_model=FriendshipPendingListEnvelope)
def list_friendship_requests(
        session: SessionDep,
        current_user: User = Depends(get_user),
        direction: FriendshipDirection = Query(
            default=FriendshipDirection.incoming,
            description="Request direction. Allowed: incoming, outgoing.",
        ),
        cursor: str | None = Query(
            default=None,
            description=CURSOR_DESCRIPTION,
            examples=[CURSOR_EXAMPLE],
        ),
        limit: int = Query(
            default=20,
            ge=1,
            le=100,
            description="Page size. Range: 1..100.",
        ),
) -> FriendshipPendingListEnvelope:
    page = list_friendship_requests_service(
        session=session,
        actor=current_user,
        direction=direction,
        cursor=cursor,
        limit=limit,
    )
    return build_list_friendship_requests_response(
        page,
        current_user.id,
    )


@router.post("/requests/{user_id}/accept", response_model=FriendshipAcceptedEnvelope)
def accept_friendship(
        user_id: UUID,
        session: SessionDep,
        current_user: User = Depends(get_user),
) -> FriendshipAcceptedEnvelope:
    friendship = accept_friendship_request(
        session=session,
        actor=current_user,
        requester_id=user_id,
    )
    return build_accept_friendship_response(friendship, current_user.id)


@router.post("/requests/{user_id}/reject", response_model=FriendshipPendingEnvelope)
def reject_friendship(
        user_id: UUID,
        session: SessionDep,
        current_user: User = Depends(get_user),
) -> FriendshipPendingEnvelope:
    friendship = reject_friendship_request(
        session=session,
        actor=current_user,
        requester_id=user_id,
    )
    return build_reject_friendship_response(friendship, current_user.id)


@router.delete("/requests/{user_id}", response_model=FriendshipPendingEnvelope)
def cancel_friendship(
        user_id: UUID,
        session: SessionDep,
        current_user: User = Depends(get_user),
) -> FriendshipPendingEnvelope:
    friendship = cancel_friendship_request(
        session=session,
        actor=current_user,
        addressee_id=user_id,
    )
    return build_cancel_friendship_response(friendship, current_user.id)


@router.get("", response_model=FriendshipAcceptedListEnvelope)
def list_accepted_friendships(
        session: SessionDep,
        current_user: User = Depends(get_user),
        cursor: str | None = Query(
            default=None,
            description=CURSOR_DESCRIPTION,
            examples=[CURSOR_EXAMPLE],
        ),
        limit: int = Query(
            default=20,
            ge=1,
            le=100,
            description="Page size. Range: 1..100.",
        ),
) -> FriendshipAcceptedListEnvelope:
    page = list_accepted_friendships_service(
        session=session,
        actor=current_user,
        cursor=cursor,
        limit=limit,
    )
    return build_list_accepted_friendships_response(
        page,
        current_user.id,
    )


@router.delete("/{user_id}", response_model=FriendshipAcceptedEnvelope)
def remove_friendship(
        user_id: UUID,
        session: SessionDep,
        current_user: User = Depends(get_user),
) -> FriendshipAcceptedEnvelope:
    friendship = remove_friendship_service(
        session=session,
        actor=current_user,
        friend_user_id=user_id,
    )
    return build_remove_friendship_response(friendship, current_user.id)
