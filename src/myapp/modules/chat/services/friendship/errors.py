from dataclasses import dataclass

__all__ = [
    "FriendshipServiceError",
    "raise_friendship_service_error",
]


@dataclass
class FriendshipServiceError(ValueError):
    status_code: int
    code: str
    message: str
    detail: str | None = None

    def __str__(self) -> str:
        if self.detail:
            return f"{self.code}: {self.detail}"
        return self.code


def raise_friendship_service_error(
        *,
        status_code: int,
        code: str,
        message: str,
        detail: str | None = None,
) -> None:
    raise FriendshipServiceError(
        status_code=status_code,
        code=code,
        message=message,
        detail=detail,
    )
