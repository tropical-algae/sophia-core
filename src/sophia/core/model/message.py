import uuid

from llama_index.core.agent.workflow import AgentOutput, AgentStream
from llama_index.core.llms import ChatMessage, CompletionResponse
from pydantic import BaseModel, Field

from sophia.common.config import settings
from sophia.common.logging import logger
from sophia.core.agent.base import ToolBase
from sophia.core.db.models import UserAccount


class AgentRequest(BaseModel):
    model: str = Field(default=settings.GPT_DEFAULT_MODEL)
    message: str


class AgentResponse(BaseModel):
    id: str
    session_id: str
    content: str

    @classmethod
    def from_llm(cls, session_id: str, output: AgentOutput | CompletionResponse):
        id = f"chatcmpl-{uuid.uuid4().hex}"
        try:
            id = (
                output.raw.get("id", f"chatcmpl-{uuid.uuid4().hex}")  # type: ignore
                if isinstance(output, AgentOutput)
                else output.raw.id  # type: ignore
            )
        except Exception as err:
            logger.error(f"Failed to catch id from agent output: {err}")
        content = (
            output.response.content if isinstance(output, AgentOutput) else output.text
        )

        return cls(
            id=id,
            session_id=session_id,
            content=content,
        )

    async def tool_post_process(self, tools: list[type[ToolBase] | None]):
        for tool in tools:
            if tool is None:
                continue
            try:
                self.content = await tool.a_tool_post_processing_function(self.content)
            except Exception as err:
                logger.error(
                    f"Failed to run {tool.__tool_name__} post process function: {err}"
                )


class AgentResponseStream(BaseModel):
    session_id: str
    tool_names: list[str]
    delta: str
    response: str

    @classmethod
    def from_llm(cls, session_id: str, output: AgentStream) -> "AgentResponseStream":
        return cls(
            session_id=session_id,
            tool_names=[i.tool_name for i in output.tool_calls],
            delta=output.delta,
            response=output.response,
        )


class MemoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessage]


class ChatSessionRequest(BaseModel):
    session_id: str
    user: UserAccount
    is_new_session: bool
