import logging
from typing import Any

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sulguk import SULGUK_PARSE_MODE

from shared.utils.pydantic import propagate_model_kwargs_to_sub_models
from telegram_bot.utils.aiogram.factory.config import (
    BotApiConfig as ExternalBotApiConfig,
)
from telegram_bot.utils.aiogram.factory.config import (
    BotConfig as ExternalBotConfig,
)
from telegram_bot.utils.aiogram.factory.config import (
    BotReceivingUpdateConfig as ExternalBotReceivingUpdateConfig,
)


class SentryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENTRY_", extra="ignore")

    dsn: HttpUrl | None = None
    environment: str = Field("unnamed")

    def build_dsn_url(self) -> str | None:
        if self.dsn:
            return self.dsn.unicode_string()
        return None


class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOGGING_", extra="ignore")

    level: int = logging.INFO
    format: str = (
        "(%(name)s) %(asctime)s | %(levelname)-6s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    @field_validator("level", mode="before")
    @classmethod
    def resolve_logging_level(cls, value: Any) -> Any:
        if isinstance(value, str):
            level: int | None = logging.getLevelNamesMapping().get(value.upper())
            if level:
                value = level
            else:
                error_msg = f"Unknown logging level: {value}"
                raise ValueError(error_msg)
        return value


class BotConfig(ExternalBotConfig, BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_", extra="ignore")

    parse_mode: str = SULGUK_PARSE_MODE


class BotApiConfig(ExternalBotApiConfig, BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_API_", extra="ignore")


class BotReceivingUpdateConfig(ExternalBotReceivingUpdateConfig, BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_RECEIVING_UPDATE_", extra="ignore")


class Config(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    bot: BotConfig
    bot_api: BotApiConfig
    bot_receiving_update: BotReceivingUpdateConfig

    sentry: SentryConfig
    logging: LoggingConfig

    force_nest_asyncio: bool = False

    def __init__(self, *args, **kwargs):
        propagate_model_kwargs_to_sub_models(self=self, init_kwargs=kwargs)
        super().__init__(*args, **kwargs)
