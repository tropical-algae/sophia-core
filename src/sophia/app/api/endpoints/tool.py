from fastapi import APIRouter, Depends, Security
from sqlmodel.ext.asyncio.session import AsyncSession

from sophia.core.agent.store import sophia_store

router = APIRouter()


@router.get("/list")
async def get_session_list() -> list[str]:
    tools: list = sophia_store.get_tool_names()
    return tools
