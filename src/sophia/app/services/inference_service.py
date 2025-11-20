import json
from collections.abc import AsyncIterator

from llama_index.core.memory import Memory

from sophia.common.util import async_db_wrapper
from sophia.core.agent.agent import SophiaAgent
from sophia.core.agent.factory import agent_factory
from sophia.core.agent.store import sophia_store
from sophia.core.db.crud.session_crud import delete_session
from sophia.core.model.message import AgentRequest, ChatSessionRequest


async def agent_stream_response(
    chat_session: ChatSessionRequest, query: AgentRequest
) -> AsyncIterator[bytes]:
    try:
        memory: Memory = sophia_store.get_memory(
            user_id=chat_session.user.id,
            session_id=chat_session.session_id,
        )
        tools: list = sophia_store.get_tools(
            blocked_tools=query.blocked_tools, is_tool_base=False
        )
        agent: SophiaAgent = agent_factory.get_agent(agent=SophiaAgent, model=query.model)

        async for resp in agent.run_stream(
            message=query.message, memory=memory, tools=tools
        ):
            yield (
                json.dumps(resp.model_dump(), ensure_ascii=False).encode("utf-8") + b"\n"
            )
    except Exception:
        if chat_session.is_new_session:
            await async_db_wrapper(delete_session, session_id=chat_session.session_id)
            return
