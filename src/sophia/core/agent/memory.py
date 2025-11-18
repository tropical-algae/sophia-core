from llama_index.core.memory import (
    BaseMemoryBlock,
    FactExtractionMemoryBlock,
    InsertMethod,
    Memory,
    StaticMemoryBlock,
    VectorMemoryBlock,
)
from llama_index.llms.openai import OpenAI

from sophia.common.config import settings
from sophia.common.logging import logger
from sophia.core.db.session import local_engine


class SophiaMemory:
    def __init__(
        self,
        api_key: str,
        api_base: str,
        default_model: str,
    ):
        self.llm = OpenAI(
            api_key=api_key,
            api_base=api_base,
            model=default_model,
            max_retries=3,
            timeout=20,
        )
        self.emb = None
        self.memories: dict[str, Memory] = {}

    def _gen_memory_blocks(self, static_content: str) -> list[BaseMemoryBlock]:
        return [
            StaticMemoryBlock(
                name="UserProfile",
                static_content=static_content,
                priority=0,
            ),
            FactExtractionMemoryBlock(
                name="ExtractedFacts",
                llm=self.llm,
                max_facts=200,
                priority=1,
            ),
        ]

    def _get_user_profile(self, user_id: str) -> str:
        _ = user_id
        return ""

    def get_memory(self, user_id: str, session_id: str) -> Memory:
        return self.memories.setdefault(
            session_id,
            Memory.from_defaults(
                session_id=session_id,
                async_database_uri=settings.SQL_DATABASE_URI,
                table_name=settings.AGENT_MEMORY_SQL_TABLE,
                async_engine=local_engine,
                token_limit=1200,
                chat_history_token_ratio=0.7,
                token_flush_size=800,
                memory_blocks=self._gen_memory_blocks(
                    static_content=self._get_user_profile(user_id=user_id)
                ),
                insert_method=InsertMethod.USER,
            ),
        )


sophia_memory = SophiaMemory(
    api_key=settings.GPT_API_KEY,
    api_base=settings.GPT_BASE_URL,
    default_model=settings.GPT_DEFAULT_MODEL,
)
