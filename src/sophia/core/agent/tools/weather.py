# from enum import Enum
# from typing import Annotated
# from sophia.core.agent.base import ToolBase
# from sophia.common.logging import logger


# class WeatherDataType(str, Enum):
#     REALTIME = "今日天气"
#     FORECAST = "天气预报"


# class WeatherTool(ToolBase):
#     __tool_name__ = "weather_tool"
#     __tool_description__ = "根据参数获取某地区 今日/未来 的天气信息"
#     __is_async__ = True

#     @staticmethod
#     # @exception_handling(default_return="无法获取该地区的天气信息")
#     async def a_tool_function(
#         data_type: Annotated[WeatherDataType, "天气数据的类型"],
#         location: Annotated[str, "省份或地区"],
#     ) -> str:
#         data_type = WeatherDataType(data_type)
#         logger.info(f"准备获取天气信息{location}-{data_type}")

#         return f"{location}地区天气为：多云转晴"
