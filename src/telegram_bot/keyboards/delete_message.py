from functools import lru_cache

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

DELETE_MESSAGE_CALLBACK_DATA = "delete_message"


@lru_cache
def delete_message_keyboard(text: str = "\N{WHITE HEAVY CHECK MARK}") -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text=text, callback_data=DELETE_MESSAGE_CALLBACK_DATA)
    return keyboard_builder.as_markup()
