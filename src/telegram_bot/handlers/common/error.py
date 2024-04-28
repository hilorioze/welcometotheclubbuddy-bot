import logging

from aiogram import Bot, Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import CallbackQuery, ErrorEvent, Message, TelegramObject
from sentry_sdk import capture_exception

from telegram_bot.keyboards.delete_message import delete_message_keyboard

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.error(ExceptionTypeFilter(Exception))
async def on_unknown_error_handler(
    event: ErrorEvent,
    bot: Bot,
) -> None:
    capture_exception(event.exception)
    logger.critical("Critical error: %s", event.exception, exc_info=event.exception)

    update_event: TelegramObject = event.update.event

    if isinstance(update_event, Message | CallbackQuery):
        await update_event.answer(
            "An unknown critical error occurred, this incident has been reported.",
            reply_markup=delete_message_keyboard(),
            parse_mode=bot.parse_mode,
        )
