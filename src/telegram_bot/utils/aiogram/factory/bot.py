from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.session.base import BaseSession
from aiogram.client.telegram import (
    PRODUCTION as TELEGRAM_API_PRODUCTION_SERVER,
)
from aiogram.client.telegram import (
    TEST as TELEGRAM_API_TEST_SERVER,
)
from aiogram.client.telegram import (
    TelegramAPIServer,
)
from sulguk import SULGUK_PARSE_MODE, AiogramSulgukMiddleware

from shared.utils.modules import json
from telegram_bot.middlewares.request.retry_request import RetryRequestMiddleware
from telegram_bot.utils.aiogram.factory.config import BotApiConfig, BotApiTypeEnum, BotConfig
from telegram_bot.utils.aiogram.specific_error.middleware import SpecifyErrorRequestMiddleware


def build_telegram_api_server(config: BotApiConfig) -> TelegramAPIServer:
    if config.type == BotApiTypeEnum.PRODUCTION:
        return TELEGRAM_API_PRODUCTION_SERVER

    if config.type == BotApiTypeEnum.TEST:
        return TELEGRAM_API_TEST_SERVER

    if config.type in (BotApiTypeEnum.LOCAL, BotApiTypeEnum.CUSTOM):
        if not config.base_url:
            error_msg = f"Base URL is required for Bot API type: {config.type}"
            raise ValueError(error_msg)

        is_local: bool = config.type == BotApiTypeEnum.LOCAL

        if not config.file_url:
            return TelegramAPIServer.from_base(config.base_url, is_local=is_local)

        return TelegramAPIServer(base=config.base_url, file=config.file_url, is_local=is_local)

    error_msg = f"Unknown Bot API type: {config.type}"
    raise ValueError(error_msg)


def create_bot_session(telegram_api_server: TelegramAPIServer | None = None) -> BaseSession:
    bot_session: BaseSession = AiohttpSession(
        api=telegram_api_server,
        json_loads=json.loads,
        json_dumps=json.dumps,
    )
    bot_session.middleware(SpecifyErrorRequestMiddleware())
    bot_session.middleware(RetryRequestMiddleware())
    return bot_session


def create_bot_properties(parse_mode: str = SULGUK_PARSE_MODE) -> DefaultBotProperties:
    bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=parse_mode)
    return bot_properties


def create_bot(bot_config: BotConfig, bot_api_config: BotApiConfig) -> Bot:
    telegram_api_server: TelegramAPIServer = build_telegram_api_server(bot_api_config)
    bot_session: BaseSession = create_bot_session(telegram_api_server=telegram_api_server)
    bot_properties: DefaultBotProperties = create_bot_properties()
    bot: Bot = Bot(
        token=bot_config.token.get_secret_value(),
        session=bot_session,
        default=bot_properties,
    )
    bot.session.middleware(AiogramSulgukMiddleware())
    return bot
