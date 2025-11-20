from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from sophia.app.api.deps import get_agent_query, get_session_id
from sophia.app.services.inference_service import agent_stream_response
from sophia.common.config import settings
from sophia.core.model.message import ChatCompleteRequest
from sophia.core.model.user import ScopeType

router = APIRouter()


@router.get("/list")
async def get_agent_models() -> list[str]:
    return settings.AGENT_OPTIONAL_MODELS


@router.post("/chat/stream")
async def agent_chat_stream(
    chat_request: ChatCompleteRequest = Depends(
        get_agent_query(scopes=[ScopeType.ADMIN, ScopeType.USER])
    ),
):
    return StreamingResponse(agent_stream_response(chat_request=chat_request))
