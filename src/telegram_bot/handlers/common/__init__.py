from aiogram import Router

from . import callback, chat, error, start

router = Router(name=__name__)
router.include_router(error.router)
router.include_router(callback.router)
router.include_router(start.router)
router.include_router(chat.router)

__all__ = ("router",)
