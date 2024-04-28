from aiogram import Bot, Dispatcher
from aiogram.webhook import aiohttp_server as aiogram_aiohttp_server
from aiogram.webhook.aiohttp_server import BaseRequestHandler, SimpleRequestHandler
from aiohttp import web

from telegram_bot.utils.aiogram.factory.config import (
    BotReceivingUpdateConfig,
    BotReceivingUpdateModeEnum,
)


def create_webhook_application(
    bot: Bot,
    dispatcher: Dispatcher,
    config: BotReceivingUpdateConfig,
) -> web.Application:
    webhook_application: web.Application = web.Application()

    webhook_requests_handler: BaseRequestHandler = SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=config.secret_token.get_secret_value(),
    )
    webhook_requests_handler.register(
        webhook_application,
        path=config.path,
    )

    aiogram_aiohttp_server.setup_application(webhook_application, dispatcher, bot=bot)

    return webhook_application


async def setup_receiving_updates(
    bot: Bot,
    config: BotReceivingUpdateConfig,
    *,
    allowed_updates: list[str] | None = None,
    drop_pending_updates: bool | None = False,
):
    if config.mode == BotReceivingUpdateModeEnum.POLLING:
        await bot.delete_webhook(drop_pending_updates=drop_pending_updates)
        return

    if config.mode == BotReceivingUpdateModeEnum.WEBHOOK:
        await bot.set_webhook(
            url=config.build_webhook_url(),
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            secret_token=config.secret_token.get_secret_value(),
        )
        return

    error_msg = f"Unknown Bot Receiving Update mode: {config.mode}"
    raise ValueError(error_msg)
