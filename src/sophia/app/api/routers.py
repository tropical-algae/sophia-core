from fastapi import APIRouter

from sophia.app.api.endpoints import base, user

router = APIRouter()
router.include_router(base.router, prefix="/system", tags=["system status"])
router.include_router(user.router, prefix="/user", tags=["user"])
