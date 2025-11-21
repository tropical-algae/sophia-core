import uuid

from llama_index.core.agent.workflow import AgentOutput, AgentStream
from llama_index.core.llms import ChatMessage, CompletionResponse
from pydantic import BaseModel, Field

from sophia.common.config import settings
from sophia.common.logging import logger
from sophia.core.agent.base import ToolBase
from sophia.core.db.models import UserAccount
from sophia.core.model.tool import AgentToolInfo


class ChatSessionRequest(BaseModel):
    session_id: str | None


class ChatSessionCompleteRequest(ChatSessionRequest):
    user: UserAccount
    is_new_session: bool


class ChatRequest(ChatSessionRequest):
    message: str
    model: str = Field(default=settings.GPT_DEFAULT_MODEL)
    blocked_tools: list[str] = Field(default_factory=list)
    use_memory: bool = Field(default=True)


class ChatCompleteRequest(ChatRequest, ChatSessionCompleteRequest):
    pass


class AgentResponse(BaseModel):
    id: str
    session_id: str | None
    tools_call: list[type[ToolBase]]
    tools: list[AgentToolInfo]
    content: str

    @classmethod
    def from_llm(
        cls,
        session_id: str | None,
        output: AgentOutput,
        tools_map: dict[str, type[ToolBase]],
    ) -> "AgentResponse":
        id = f"chatcmpl-{uuid.uuid4().hex}"
        try:
            id = output.raw.get("id", f"chatcmpl-{uuid.uuid4().hex}")  # type: ignore
        except Exception as err:
            logger.error(f"Failed to catch id from agent output: {err}")

        tools_call = []
        tools_call_info = []
        for call in output.tool_calls:
            if tool := tools_map.get(call.tool_name):
                tools_call.append(tool)
                tools_call_info.append(tool.__tool_info__)
        return cls(
            id=id,
            session_id=session_id,
            tools=tools_call_info,
            tools_call=tools_call,
            content=output.response.content,
        )

    async def tool_post_process(self):
        try:
            for tool in self.tools_call:
                self.content = await tool.a_tool_post_processing_function(self.content)
        except Exception as err:
            logger.error(f"Failed to run tool post process function: {err}")
            raise


class AgentResponseStream(BaseModel):
    session_id: str | None
    tools: list[AgentToolInfo]
    delta: str
    response: str

    @classmethod
    def from_llm(
        cls,
        session_id: str | None,
        output: AgentStream,
        tools_map: dict[str, type[ToolBase]],
    ) -> "AgentResponseStream":
        tools: list[AgentToolInfo] = []
        for call in output.tool_calls:
            tool = tools_map.get(call.tool_name)
            if tool:
                tools.append(tool.__tool_info__)
        return cls(
            session_id=session_id,
            tools=tools,
            delta=output.delta,
            response=output.response,
        )


class MemoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessage]
