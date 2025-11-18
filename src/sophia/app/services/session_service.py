from llama_index.core.memory import Memory
from sqlmodel.ext.asyncio.session import AsyncSession

from sophia.common.util import generate_random_token
from sophia.core.agent.agent import agent
from sophia.core.db.crud.session_crud import insert_session
from sophia.core.db.models import UserAccount
from sophia.core.model.message import MemoryResponse


async def create_session(db: AsyncSession, user: UserAccount) -> str:
    session_id: str = generate_random_token(prefix="SESS", length=16)
    # 插入session id和user的映射
    await insert_session(db=db, session_id=session_id, user_id=user.id)

    return session_id


async def collect_session_memory(session_id: str) -> MemoryResponse:
    memory: Memory | None = agent.get_memory(session_id=session_id)
    messages = await memory.aget_all() if memory else []
    return MemoryResponse(session_id=session_id, messages=messages)
