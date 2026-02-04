import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers import setup_handlers
from database.models import init_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_health_server() -> None:
    app = web.Application()

    async def health(_: web.Request) -> web.Response:
        return web.Response(text="ok")

    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health server started on port %s", port)


async def start_bot() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Update .env file.")

    init_db()

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    setup_handlers(dp)

    logger.info("Starting Metallica Archive Bot...")
    await dp.start_polling(bot)


async def main():
    await asyncio.gather(
        start_health_server(),
        start_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
