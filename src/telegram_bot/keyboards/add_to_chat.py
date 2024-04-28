from functools import lru_cache

from aiogram.utils.deep_linking import create_deep_link
from aiogram.utils.keyboard import InlineKeyboardButton


@lru_cache
def add_to_chat_button(bot_username: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="Add to Chat",
        url=create_deep_link(bot_username, link_type="startgroup", payload="start"),
    )
