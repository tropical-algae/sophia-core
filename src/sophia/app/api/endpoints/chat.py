from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from sophia.app.api.deps import get_session_id
from sophia.app.services.inference_service import agent_stream_response
from sophia.common.config import settings
from sophia.core.model.message import AgentRequest, ChatSessionRequest
from sophia.core.model.user import ScopeType

router = APIRouter()


@router.get("/models")
async def get_agent_models() -> list[str]:
    return settings.AGENT_OPTIONAL_MODELS


@router.post("/agent/stream")
async def agent_chat_stream(
    data: AgentRequest,
    chat_session: ChatSessionRequest = Depends(
        get_session_id(scopes=[ScopeType.ADMIN, ScopeType.USER], auto_create_session=True)
    ),
):
    return StreamingResponse(agent_stream_response(chat_session=chat_session, query=data))
