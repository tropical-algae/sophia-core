from fastapi import APIRouter, Depends, Security
from sqlmodel.ext.asyncio.session import AsyncSession

from sophia.app.api.deps import get_current_user, get_db, get_session_id
from sophia.app.services.session_service import collect_session_memory, create_session
from sophia.core.db.models import UserAccount
from sophia.core.model.message import AgentRequest, ChatSessionRequest
from sophia.core.model.user import ScopeType

router = APIRouter()


@router.post("/messages")
async def get_session_messages(
    chat_session: ChatSessionRequest = Depends(
        get_session_id(
            scopes=[ScopeType.ADMIN, ScopeType.USER], auto_create_session=False
        )
    ),
):
    return await collect_session_memory(session_id=chat_session.session_id)
