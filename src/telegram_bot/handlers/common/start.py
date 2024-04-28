from typing import TYPE_CHECKING

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from shared.utils.jinja.utils import async_render_text
from telegram_bot.common import JINJA_MIDDLEWARE_KEY
from telegram_bot.keyboards.add_to_chat import add_to_chat_button

if TYPE_CHECKING:
    from jinja2 import Environment

router = Router(name=__name__)


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot, **kwargs):
    bot_username: str | None = (await bot.get_me()).username
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = (
        InlineKeyboardBuilder().add(add_to_chat_button(bot_username)).as_markup()
        if bot_username
        else None
    )

    jinja_environment: Environment = kwargs[JINJA_MIDDLEWARE_KEY]
    await message.reply(
        await async_render_text(
            "An inimitable and unique bot that will greet your fucking slaves when they join to chat.",
            environment=jinja_environment,
        ),
        reply_markup=reply_markup,
        parse_mode=bot.parse_mode,
    )
