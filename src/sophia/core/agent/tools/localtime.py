from datetime import datetime

from sophia.common.logging import logger
from sophia.core.agent.base import ToolBase


class LocaltimeTool(ToolBase):
    __tool_name__ = "check_time"
    __tool_description__ = "获取当前时间"
    __activate__ = True

    @staticmethod
    # @exception_handling(default_return="不清楚当前时间")
    async def a_tool_function() -> str:
        localtime = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {datetime.now().strftime('%A')}"
        logger.info(f"工具调用：检查当前时间 {localtime}")
        return localtime
