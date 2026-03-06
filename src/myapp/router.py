from fastapi import APIRouter

from myapp.modules import chat
from myapp.modules import profiles

router = APIRouter(prefix="/api", )

router.include_router(profiles.api_router)
router.include_router(chat.api_router)
