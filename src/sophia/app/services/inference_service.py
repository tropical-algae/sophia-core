import json
from collections.abc import AsyncIterator

from llama_index.core.memory import Memory

from sophia.common.util import async_db_wrapper
from sophia.core.agent.agent import sophia_agent
from sophia.core.agent.memory import sophia_memory
from sophia.core.db.crud.session_crud import delete_session
from sophia.core.model.message import ChatSessionRequest


async def agent_stream_response(
    chat_session: ChatSessionRequest, message: str
) -> AsyncIterator[bytes]:
    try:
        memory: Memory | None = sophia_memory.get_memory(
            user_id=chat_session.user.id,
            session_id=chat_session.session_id,
        )
        if memory is None:
            return
        async for resp in sophia_agent.run_stream(message=message, memory=memory):
            yield (
                json.dumps(resp.model_dump(), ensure_ascii=False).encode("utf-8") + b"\n"
            )
    except Exception:
        if chat_session.is_new_session:
            await async_db_wrapper(delete_session, session_id=chat_session.session_id)
            return
