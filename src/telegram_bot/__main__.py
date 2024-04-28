import asyncio
import logging
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiohttp import web
from sentry_sdk.integrations.logging import LoggingIntegration

from shared.config.factory import load_from_dotenv_filename
from shared.interfaces.asyncio import CoroutineLike
from shared.tools.taskmanager import TaskManager
from shared.utils.jinja.factory import create_jinja_environment
from shared.utils.logging import configure_logging
from shared.utils.modules import get_loop
from shared.utils.sentry import format_release, initialize_sentry
from telegram_bot import __version__
from telegram_bot.common import JINJA_MIDDLEWARE_KEY
from telegram_bot.handlers import router as handlers_router
from telegram_bot.utils.aiogram.commands import set_bot_commands
from telegram_bot.utils.aiogram.event_context import UserContextMiddleware
from telegram_bot.utils.aiogram.factory.bot import create_bot
from telegram_bot.utils.aiogram.factory.config import (
    BotReceivingUpdateConfig,
    BotReceivingUpdateModeEnum,
)
from telegram_bot.utils.aiogram.factory.dispatcher import (
    create_dispatcher_memory_storage,
    create_dispatcher_simple_events_isolation,
)
from telegram_bot.utils.aiogram.factory.webhook import (
    create_webhook_application,
    setup_receiving_updates,
)

if TYPE_CHECKING:
    from jinja2 import Environment

logger = logging.getLogger(__name__)


def create_dispatcher() -> Dispatcher:
    dispatcher_events_isolation = create_dispatcher_simple_events_isolation()
    dispatcher_storage = create_dispatcher_memory_storage()
    dispatcher = Dispatcher(
        storage=dispatcher_storage,
        events_isolation=dispatcher_events_isolation,
    )

    dispatcher.update.middleware(UserContextMiddleware())

    dispatcher.include_router(handlers_router)

    return dispatcher


async def on_startup(
    bot: Bot,
    *,
    receiving_update_config: BotReceivingUpdateConfig,
    drop_pending_updates: bool = False,
    allowed_updates: list[str] | None = None,
) -> None:
    await setup_receiving_updates(
        bot=bot,
        config=receiving_update_config,
        allowed_updates=allowed_updates,
        drop_pending_updates=drop_pending_updates,
    )
    await set_bot_commands(bot=bot)


def start_receiving_updates(
    bot: Bot,
    dispatcher: Dispatcher,
    *,
    webhook_application: web.Application,
    receiving_update_config: BotReceivingUpdateConfig,
    allowed_updates: list[str] | None = None,
) -> CoroutineLike:
    if receiving_update_config.mode == BotReceivingUpdateModeEnum.POLLING:
        return dispatcher.start_polling(
            bot,
            allowed_updates=allowed_updates or dispatcher.resolve_used_update_types(),
            handle_signals=False,
        )

    if receiving_update_config.mode == BotReceivingUpdateModeEnum.WEBHOOK:
        return web._run_app(
            app=webhook_application,
            host=receiving_update_config.host,
            port=receiving_update_config.port,
            handle_signals=False,
        )

    error_msg = f"Receiving Update Mode: {receiving_update_config.mode}"
    raise NotImplementedError(error_msg)


def main() -> None:
    config = load_from_dotenv_filename()
    loop = get_loop(force_nest_asyncio=config.force_nest_asyncio)
    asyncio.set_event_loop(loop)

    configure_logging(level=config.logging.level, format=config.logging.format)

    initialize_sentry(
        sentry_dsn=config.sentry.build_dsn_url(),
        sentry_environment=config.sentry.environment,
        release=format_release(__package__, __version__),
        integrations=[
            LoggingIntegration(level=logging.INFO, event_level=logging.WARNING),
        ],
    )

    jinja_environment: Environment = create_jinja_environment()
    bot: Bot = create_bot(bot_config=config.bot, bot_api_config=config.bot_api)
    dispatcher: Dispatcher = create_dispatcher()
    dispatcher[JINJA_MIDDLEWARE_KEY] = jinja_environment
    webhook_application: web.Application = create_webhook_application(
        bot=bot,
        dispatcher=dispatcher,
        config=config.bot_receiving_update,
    )

    drop_pending_updates: bool = False
    allowed_updates: list[str] = dispatcher.resolve_used_update_types()

    logger.info(
        "Bot Receiving Update Mode: %s",
        config.bot_receiving_update.mode,
    )

    task_manager = TaskManager()
    task_manager.add_task_on_startup(
        on_startup(
            bot=bot,
            receiving_update_config=config.bot_receiving_update,
            drop_pending_updates=drop_pending_updates,
            allowed_updates=allowed_updates,
        ),
    )
    task_manager.add_task(
        start_receiving_updates(
            bot=bot,
            dispatcher=dispatcher,
            receiving_update_config=config.bot_receiving_update,
            webhook_application=webhook_application,
            allowed_updates=allowed_updates,
        ),
    )
    task_manager.run(loop=loop)


if __name__ == "__main__":
    main()
