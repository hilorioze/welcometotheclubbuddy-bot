from aiogram import Router

from . import member

router = Router(name=__name__)
router.include_router(member.router)


__all__ = ("router",)
