from aiogram import Dispatcher

from bot.handlers import commands, callbacks


def setup_handlers(dp: Dispatcher):
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)


__all__ = ["setup_handlers"]
