from aiogram import Router

from . import common

router = Router(name=__name__)
router.include_router(common.router)

__all__ = ("router",)
