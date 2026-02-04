from aiogram import Router

router = Router()

from bot.handlers import commands, callbacks

def setup_handlers(dp: Router):
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)

__all__ = ["router", "setup_handlers"]
