import json
from collections.abc import AsyncIterator

from fastapi import HTTPException
from llama_index.core.memory import Memory

from sophia.app.utils.constant import CONSTANT
from sophia.common.util import async_db_wrapper
from sophia.core.agent.agent import SophiaAgent
from sophia.core.agent.factory import agent_factory
from sophia.core.agent.store import sophia_store
from sophia.core.db.crud.session_crud import delete_session
from sophia.core.model.message import ChatCompleteRequest


async def agent_stream_response(
    chat_request: ChatCompleteRequest,
) -> AsyncIterator[bytes]:
    try:
        memory: Memory | None = None
        if chat_request.use_memory:
            if not chat_request.session_id:
                raise HTTPException(**CONSTANT.RESP_USER_SESSION_NULL)
            memory = sophia_store.get_memory(
                user_id=chat_request.user.id,
                session_id=chat_request.session_id,
            )

        tools: list = sophia_store.get_tools(
            blocked_tools=chat_request.blocked_tools, is_tool_base=False
        )
        agent: SophiaAgent = agent_factory.get_agent(
            agent=SophiaAgent, model=chat_request.model
        )

        async for resp in agent.run_stream(
            message=chat_request.message, memory=memory, tools=tools
        ):
            yield (
                json.dumps(resp.model_dump(), ensure_ascii=False).encode("utf-8") + b"\n"
            )
    except Exception:
        if chat_request.is_new_session and chat_request.use_memory:
            await async_db_wrapper(delete_session, session_id=chat_request.session_id)
            return
