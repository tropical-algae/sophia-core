from fastapi import APIRouter

from sophia.app.api.endpoints import chat, health, session, user

router = APIRouter()
router.include_router(health.router, prefix="/system", tags=["system status"])
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(chat.router, prefix="/chat", tags=["chat with agent/llm"])
router.include_router(session.router, prefix="/session", tags=["chat session"])
