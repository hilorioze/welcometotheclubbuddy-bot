from aiogram import Bot
from aiogram.client.session.middlewares.base import (
    BaseRequestMiddleware,
    NextRequestMiddlewareType,
)
from aiogram.exceptions import TelegramAPIError
from aiogram.methods import Response, TelegramMethod
from aiogram.methods.base import TelegramType

from telegram_bot.utils.aiogram.specific_error.exceptions import SpecificAPIError


class SpecifyErrorRequestMiddleware(BaseRequestMiddleware):
    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        try:
            response = await make_request(bot, method)
        except TelegramAPIError as exception:
            error = SpecificAPIError.specify_error(exception)
            raise error from exception
        return response
