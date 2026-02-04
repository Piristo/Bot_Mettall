import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from database.models import AsyncSessionLocal, init_db
from database.repository import VideoRepository, SyncStatusRepository
from services.youtube.search import YouTubeCrawler
from services.classifier.content import ContentClassifier
from services.quality.scorer import QualityScorer
from utils.tour_detector import TourDetector
from bot.config import SYNC_INTERVAL_HOURS
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.crawler = YouTubeCrawler()
    
    async def sync_videos(self):
        logger.info("Starting scheduled YouTube sync...")
        
        try:
            videos_found = await self.crawler.sync_to_database()
            
            async with AsyncSessionLocal() as session:
                repo = SyncStatusRepository(session)
                await repo.update_status(videos_added=videos_found, status="completed")
            
            logger.info(f"Sync completed. Found {videos_found} new videos.")
            return videos_found
        
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            async with AsyncSessionLocal() as session:
                repo = SyncStatusRepository(session)
                await repo.update_status(videos_added=0, status="failed", error=str(e))
            return 0
    
    async def check_and_sync(self):
        async with AsyncSessionLocal() as session:
            repo = SyncStatusRepository(session)
            last_sync = await repo.get_last_sync()
        
        if last_sync:
            next_sync = last_sync.last_sync + timedelta(hours=SYNC_INTERVAL_HOURS)
            if datetime.utcnow() < next_sync:
                logger.info(f"Skipping sync. Next sync at {next_sync}")
                return
        
        await self.sync_videos()
    
    def setup(self):
        self.scheduler.add_job(
            self.check_and_sync,
            CronTrigger(hour=3, minute=0),
            id='daily_youtube_sync',
            name='Daily YouTube video sync',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Scheduler started")

async def run_initial_sync():
    logger.info("Running initial YouTube sync...")
    scheduler = Scheduler()
    count = await scheduler.sync_videos()
    logger.info(f"Initial sync completed. Added {count} videos.")
    return count

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        asyncio.run(run_initial_sync())
    else:
        init_db()
        scheduler = Scheduler()
        scheduler.setup()
        
        from bot.main import main
        asyncio.run(main())
