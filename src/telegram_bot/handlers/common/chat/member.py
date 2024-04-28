from typing import TYPE_CHECKING

from aiogram import Bot, Router
from aiogram.filters import JOIN_TRANSITION, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from shared.utils.jinja.utils import async_render_text
from telegram_bot.common import JINJA_MIDDLEWARE_KEY

if TYPE_CHECKING:
    from jinja2 import Environment

router = Router(name=__name__)


@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_member_handler(event: ChatMemberUpdated, bot: Bot, **kwargs):
    jinja_environment: Environment = kwargs[JINJA_MIDDLEWARE_KEY]
    await event.answer(
        await async_render_text(
            """
                Congratulations, you are officially part of the band.<br>
                Welcome to the club, <a href="{{ user_url }}">buddy</a>!
                """,
            environment=jinja_environment,
            user_url=event.new_chat_member.user.url,
        ),
        parse_mode=bot.parse_mode,
    )
