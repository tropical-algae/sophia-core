import json
from collections.abc import AsyncIterator

from sophia.common.util import async_db_wrapper
from sophia.core.agent.agent import agent
from sophia.core.db.crud.session_crud import delete_session
from sophia.core.model.message import ChatSessionRequest


async def agent_stream_response(
    chat_session: ChatSessionRequest, message: str
) -> AsyncIterator[bytes]:
    try:
        async for resp in agent.run_stream(
            session_id=chat_session.session_id, message=message
        ):
            yield (
                json.dumps(resp.model_dump(), ensure_ascii=False).encode("utf-8") + b"\n"
            )
    except Exception:
        if chat_session.is_new_session:
            await async_db_wrapper(delete_session, session_id=chat_session.session_id)
            return
