from fastapi import APIRouter

from handlers.admin_handlers import admin_router
from handlers.user_handlers import user_router


api_router = APIRouter()
api_router.include_router(admin_router, prefix="/admin")
api_router.include_router(user_router, prefix="/user", tags=["User"])
