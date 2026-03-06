from fastapi import APIRouter

from . import friendship

__all__ = ["router"]

router = APIRouter()
router.include_router(friendship.router)
