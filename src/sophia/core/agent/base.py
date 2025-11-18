from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from llama_index.core.memory import Memory
from llama_index.core.tools import FunctionTool


class AgentBase(ABC):
    @abstractmethod
    async def run(
        self,
        message: str,
        memory: Memory,
        use_agent: bool = True,
        **kwargs,  # type: ignore
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    def run_stream(
        self,
        message: str,
        memory: Memory,
        use_agent: bool = True,
        **kwargs,  # type: ignore
    ) -> AsyncIterator[Any]:
        raise NotImplementedError


class ToolBase(ABC):
    __tool_name__: str = ""
    __tool_description__: str = ""
    __activate__: bool = True

    @staticmethod
    @abstractmethod
    async def a_tool_function(*args, **kwargs) -> Any:
        raise NotImplementedError

    @staticmethod
    async def a_tool_post_processing_function(agent_message: str) -> str:
        return agent_message

    @classmethod
    def get_tool(cls) -> Any:
        return FunctionTool.from_defaults(
            name=cls.__tool_name__,
            description=cls.__tool_description__,
            async_fn=cls.a_tool_function,
        )
