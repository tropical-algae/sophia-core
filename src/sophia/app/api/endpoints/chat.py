from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from sophia.app.services.model_interaction import agent_stream_response
from sophia.core.model.message import AgentRequest

router = APIRouter()


@router.post("/agent/stream")
async def agent_chat_stream(data: AgentRequest):
    return StreamingResponse(
        agent_stream_response(session_id=data.session_id, message=data.message)
    )
