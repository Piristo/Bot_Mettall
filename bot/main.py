import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers import setup_handlers
from database.models import init_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Update .env file.")

    init_db()

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    setup_handlers(dp)

    logger.info("Starting Metallica Archive Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
