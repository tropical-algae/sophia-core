import inspect
from collections.abc import AsyncIterator
from typing import TypeVar, cast

from llama_index.core.agent.workflow import (
    AgentOutput,
    AgentStream,
    FunctionAgent,
    ReActAgent,
)
from llama_index.core.memory import Memory
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

from sophia.common.config import settings
from sophia.common.decorator import exception_handling
from sophia.common.logging import logger
from sophia.core.agent.base import AgentBase, ToolBase
from sophia.core.model.message import AgentResponse, AgentResponseStream

T = TypeVar("T", bound=ToolBase)


class SophiaAgent(AgentBase):
    def __init__(
        self,
        api_key: str,
        api_base: str,
        default_model: str,
        max_retries: int = 3,
        timeout: int = 30,
        system_prompt: str = "You are a helpful assistant",
        **kwargs,
    ):
        self.client = OpenAI(
            api_key=api_key,
            api_base=api_base,
            model=default_model,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs,
        )
        self.context: dict[str, Context] = {}
        self.system_prompt = system_prompt

    @exception_handling
    async def run(
        self,
        message: str,
        memory: Memory,
        tools: list[type[ToolBase]],
        use_agent: bool = True,
        **kwargs,
    ) -> AgentResponse | None:
        result: AgentResponse | None = None
        fn_tools = [t.get_tool() for t in tools]
        if use_agent:
            agent = FunctionAgent(
                system_prompt=self.system_prompt,
                tools=fn_tools,
                llm=self.client,
            )
            response: AgentOutput = await agent.run(
                user_msg=message, memory=memory, **kwargs
            )
            # 封装结果
            result = AgentResponse.from_llm(session_id=memory.session_id, output=response)
            result.tool_post_process(
                [tool for tool in tools if tool.__tool_name__ in response.tool_calls]
            )
            return result

        response = await self.client.achat(messages=memory.aget_all(), **kwargs)
        result = AgentResponse.from_llm(session_id=memory.session_id, output=response)
        return result

    async def run_stream(
        self,
        message: str,
        memory: Memory,
        tools: list[FunctionTool],
        use_agent: bool = True,
        **kwargs,
    ) -> AsyncIterator[AgentResponseStream]:
        _ = use_agent
        # ctx = self._get_context(session_id)
        steps = 0
        try:
            agent = FunctionAgent(
                system_prompt=self.system_prompt,
                tools=tools,
                llm=self.client,
            )
            handler = agent.run(user_msg=message, memory=memory, **kwargs)
            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    steps += 1
                    yield AgentResponseStream.from_llm(
                        session_id=memory.session_id, output=event
                    )
        finally:
            if steps == 0:
                raise RuntimeError("Agent failed to perform streaming inference.")
