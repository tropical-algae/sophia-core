import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

from sophia import __version__


class SysSetting(BaseSettings):
    # FastAPI
    VERSION: str = __version__
    PROJECT_NAME: str = "sophia"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False


class BasicSetting(BaseSettings):
    # database
    SQL_DATABASE_URI: str = ""
    SQL_POOL_PRE_PING: bool = True
    SQL_POOL_SIZE: int = 10
    SQL_MAX_OVERFLOW: int = 20
    SQL_POOL_TIMEOUT: int = 30
    SQL_POOL_RECYCLE: int = 1800

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ACCESS_TOKEN_SECRET_KEY: str = secrets.token_hex(32)


class LogSetting(BaseSettings):
    # logger
    LOG_ROOT: str = "./log"
    LOG_LEVEL: str = "INFO"
    LOG_FILE_ENCODING: str = "utf-8"
    LOG_CONSOLE_OUTPUT: bool = True


class ServiceSetting(BaseSettings):
    # service
    GPT_PROMPT_FILEPATH: str = ""
    GPT_BASE_URL: str = ""
    GPT_API_KEY: str = ""
    GPT_DEFAULT_MODEL: str = "gpt-3.5-turbo-ca"
    GPT_TEMPERATURE: float = 0.8
    GPT_RESPONSE_FORMAT: dict = {"type": "json_object"}


class Setting(SysSetting, BasicSetting, LogSetting, ServiceSetting):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Setting()
