from fastapi import APIRouter, Depends, Security
from sqlmodel.ext.asyncio.session import AsyncSession

from sophia.app.api.deps import get_current_user, get_db, get_session_id
from sophia.app.services.session_service import (
    collect_session_memory,
    collect_sessions,
    create_session,
)
from sophia.core.db.models import UserAccount
from sophia.core.model.message import AgentRequest, ChatSessionRequest, MemoryResponse
from sophia.core.model.user import ScopeType

router = APIRouter()


@router.get("/list")
async def get_session_list(
    db: AsyncSession = Depends(get_db),
    current_user: UserAccount = Security(get_current_user),
) -> list[str]:
    return await collect_sessions(db=db, user_id=current_user.id)


@router.post("/messages", response_model=MemoryResponse)
async def get_session_messages(
    chat_session: ChatSessionRequest = Depends(
        get_session_id(
            scopes=[ScopeType.ADMIN, ScopeType.USER], auto_create_session=False
        )
    ),
) -> MemoryResponse:
    return await collect_session_memory(
        user_id=chat_session.user.id, session_id=chat_session.session_id
    )
