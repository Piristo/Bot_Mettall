import asyncio
import logging

from dotenv import load_dotenv

from bot.config import YOUTUBE_API_KEY
from services.youtube.search import YouTubeCrawler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    load_dotenv()

    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set. Update .env file.")

    crawler = YouTubeCrawler()
    added = await crawler.sync_to_database()
    logger.info("Refresh completed. Added %s videos.", added)


if __name__ == "__main__":
    asyncio.run(main())
