import asyncio
import logging
from typing import Final

from aiogram import Bot
from aiogram.client.session.middlewares.base import (
    BaseRequestMiddleware,
    NextRequestMiddlewareType,
)
from aiogram.dispatcher.dispatcher import DEFAULT_BACKOFF_CONFIG
from aiogram.exceptions import (
    TelegramEntityTooLarge,
    TelegramNetworkError,
    TelegramRetryAfter,
    TelegramServerError,
)
from aiogram.methods import AnswerCallbackQuery, Response, TelegramMethod
from aiogram.methods.base import TelegramType
from aiogram.utils.backoff import Backoff, BackoffConfig

logger = logging.getLogger("aiogram.middlewares")
DEFAULT_MAX_RETRIES: Final[int] = 7


class RetryRequestMiddleware(BaseRequestMiddleware):
    def __init__(
        self,
        backoff_config: BackoffConfig = DEFAULT_BACKOFF_CONFIG,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self.backoff_config = backoff_config
        self.max_retries = max_retries

    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        backoff = Backoff(config=self.backoff_config)
        retries = 0

        while True:
            retries += 1

            try:
                response = await make_request(bot, method)
            except TelegramRetryAfter as exc:
                if isinstance(method, AnswerCallbackQuery):
                    raise

                if retries == self.max_retries:
                    raise

                logger.exception(
                    "Request '%s' failed due to rate limit. Sleeping %s seconds.",
                    type(method).__name__,
                    exc.retry_after,
                )

                backoff.reset()

                await asyncio.sleep(exc.retry_after)
            except (TelegramServerError, TelegramNetworkError) as exc:
                if isinstance(exc, TelegramEntityTooLarge):
                    raise

                if retries == self.max_retries:
                    raise

                logger.exception(
                    "Request '%s' failed due to %s - %r. Sleeping %s seconds.",
                    type(method).__name__,
                    type(exc).__name__,
                    exc,  # noqa: TRY401
                    backoff.next_delay,
                )

                await backoff.asleep()
            else:
                return response
