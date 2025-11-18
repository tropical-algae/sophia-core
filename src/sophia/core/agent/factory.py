from typing import TypeVar, cast

from fastapi import HTTPException

from sophia.app.utils.constant import CONSTANT
from sophia.common.config import settings
from sophia.core.agent.base import AgentBase

T = TypeVar("T", bound=AgentBase)


class AgentFactory:
    def __init__(self):
        self.agents: dict[str, AgentBase] = {}

    def get_agent(self, agent: type[T], model: str) -> T:
        if model not in settings.AGENT_OPTIONAL_MODELS:
            raise HTTPException(**CONSTANT.RESP_INVALID_MODEL)
        if model not in self.agents:
            self.agents[model] = agent(
                api_key=settings.GPT_API_KEY,
                api_base=settings.GPT_BASE_URL,
                default_model=model,
                system_prompt=settings.AGENT_SYS_PROMPT_SUFFIX,
            )

        return cast(T, self.agents[model])


agent_factory = AgentFactory()
