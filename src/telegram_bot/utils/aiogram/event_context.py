from aiogram import BaseMiddleware
from aiogram.dispatcher.middlewares.user_context import (
    EVENT_CHAT_KEY,
    EVENT_FROM_USER_KEY,
    EVENT_THREAD_ID_KEY,
)
from aiogram.types import Chat, Message, TelegramObject, Update, User


class UserContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event,
        data,
    ):
        chat, user, thread_id = self.resolve_event_context(event)
        data[EVENT_FROM_USER_KEY], data[EVENT_CHAT_KEY], data[EVENT_THREAD_ID_KEY] = (
            user,
            chat,
            thread_id,
        )
        return await handler(event, data)

    @classmethod
    def resolve_event_context(
        cls,
        event,
        *,
        chat: Chat | None = None,
        user: User | None = None,
        thread_id: int | None = None,
    ) -> tuple[Chat | None, User | None, int | None]:
        if (not chat) and (hasattr(event, "chat") and isinstance(event.chat, Chat)):
            chat = event.chat

        if (not user) and (hasattr(event, "from_user") and isinstance(event.from_user, User)):
            user = event.from_user

        if (not user) and (
            (hasattr(event, "is_topic_message") and event.is_topic_message)
            and (hasattr(event, "message_thread_id") and isinstance(event.message_thread_id, int))
        ):
            thread_id = event.message_thread_id

        if chat and user and thread_id:
            return chat, user, thread_id

        if hasattr(event, "message") and isinstance(event.message, Message):
            return cls.resolve_event_context(
                event.message,
                chat=chat,
                user=user,
                thread_id=thread_id,
            )

        if hasattr(event, "update") and isinstance(event.update, Update):
            return cls.resolve_event_context(
                event.update,
                chat=chat,
                user=user,
                thread_id=thread_id,
            )

        if hasattr(event, "event") and isinstance(event.event, TelegramObject):
            return cls.resolve_event_context(
                event.event,
                chat=chat,
                user=user,
                thread_id=thread_id,
            )

        return chat, user, thread_id
