import inspect
import uuid
from collections.abc import AsyncIterator
from typing import cast

from llama_index.core.agent.workflow import (
    AgentOutput,
    AgentStream,
    FunctionAgent,
    ReActAgent,
)
from llama_index.core.llms import CompletionResponse
from llama_index.core.memory import (
    BaseMemoryBlock,
    FactExtractionMemoryBlock,
    InsertMethod,
    Memory,
    StaticMemoryBlock,
    VectorMemoryBlock,
)
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

import sophia.core.agent.tools as agent_tools
from sophia.common.config import settings
from sophia.common.decorator import exception_handling
from sophia.common.logging import logger
from sophia.common.util import import_all_modules_from_package
from sophia.core.agent.base import AgentBase, ToolBase
from sophia.core.db.session import local_engine
from sophia.core.model.message import AgentResponse, AgentResponseStream


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
        self.blocks: list[BaseMemoryBlock] = [
            StaticMemoryBlock(
                name="profile",
                static_content="User prefers concise, Chinese responses.",
                priority=0,
            ),
            FactExtractionMemoryBlock(
                name="extracted facts",
                llm=self.client,
                max_facts=200,
                priority=1,
            ),
        ]
        self.tools: dict[str, type[ToolBase]] = {}
        self.context: dict[str, Context] = {}
        # register tools
        self._register_tools()
        self.agent = FunctionAgent(
            system_prompt=system_prompt,
            tools=[tool.get_tool() for tool in self.tools.values()],
            llm=self.client,
        )

    def _get_context(self, session_id: str) -> Context:
        return self.context.setdefault(session_id, Context(self.agent))

    def _register_tools(self) -> None:
        # import all tool modules
        import_all_modules_from_package(agent_tools)

        tools: dict[str, type[ToolBase]] = {}
        unactivated_tools: list[str] = []
        # collect tools
        for tool in ToolBase.__subclasses__():
            if tool.__activate__ and not inspect.isabstract(tool):
                tools[tool.__tool_name__] = cast(type[ToolBase], tool)
            else:
                unactivated_tools.append(tool.__tool_name__)

        self.tools = tools
        logger.info(f"Loaded tools: {list(self.tools.keys())}")
        logger.info(f"Unloaded tools: {unactivated_tools}")

    @exception_handling
    async def run(
        self, message: str, memory: Memory, use_agent: bool = True, **kwargs
    ) -> AgentResponse | None:
        result: AgentResponse | None = None

        if use_agent:
            ctx = self._get_context(memory.session_id)
            response: AgentOutput = await self.agent.run(
                user_msg=message, memory=memory, context=ctx, **kwargs
            )
            # 封装结果
            result = AgentResponse.from_llm(session_id=memory.session_id, output=response)
            result.tool_post_process(
                [self.tools.get(t.tool_name) for t in response.tool_calls]
            )
            return result

        response = await self.client.achat(messages=memory.aget_all(), **kwargs)
        result = AgentResponse.from_llm(session_id=memory.session_id, output=response)
        return result

    async def run_stream(
        self, message: str, memory: Memory, use_agent: bool = True, **kwargs
    ) -> AsyncIterator[AgentResponseStream]:
        _ = use_agent
        # ctx = self._get_context(session_id)
        steps = 0
        try:
            handler = self.agent.run(user_msg=message, memory=memory, **kwargs)
            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    steps += 1
                    yield AgentResponseStream.from_llm(
                        session_id=memory.session_id, output=event
                    )
        finally:
            if steps == 0:
                raise RuntimeError("Agent failed to perform streaming inference.")


sophia_agent = SophiaAgent(
    api_key=settings.GPT_API_KEY,
    api_base=settings.GPT_BASE_URL,
    default_model=settings.GPT_DEFAULT_MODEL,
    system_prompt=settings.AGENT_SYS_PROMPT_SUFFIX,
)
