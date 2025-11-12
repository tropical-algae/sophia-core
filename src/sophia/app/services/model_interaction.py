import json
from collections.abc import AsyncIterator

from sophia.core.agent.agent import agent


async def agent_stream_response(session_id: str, message: str) -> AsyncIterator[bytes]:
    async for resp in agent.run_stream(session_id=session_id, message=message):
        yield json.dumps(resp.model_dump(), ensure_ascii=False).encode("utf-8") + b"\n"
