from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from shared.utils.jinja.utils import async_render_text
from telegram_bot.common import JINJA_MIDDLEWARE_KEY
from telegram_bot.keyboards.delete_message import DELETE_MESSAGE_CALLBACK_DATA
from telegram_bot.utils.aiogram.specific_error.exceptions import MessageCantBeDeletedError

if TYPE_CHECKING:
    from jinja2 import Environment

router = Router(name=__name__)


@router.callback_query(F.data == DELETE_MESSAGE_CALLBACK_DATA)
async def delete_message_handler(
    callback_query: CallbackQuery,
    **kwargs,
):
    jinja_environment: Environment = kwargs[JINJA_MIDDLEWARE_KEY]
    try:
        if callback_query.message and isinstance(callback_query.message, Message):
            await callback_query.message.delete()
    except MessageCantBeDeletedError:
        await callback_query.answer(
            await async_render_text(
                "An error occurred while deleting message, the deletion deadline may have expired. Delete the message manually.",
                environment=jinja_environment,
            ),
        )
