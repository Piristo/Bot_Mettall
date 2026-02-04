from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/metallica.db")

MAX_RESULTS_PER_PAGE = int(os.getenv("MAX_RESULTS_PER_PAGE", 10))
SYNC_INTERVAL_HOURS = int(os.getenv("SYNC_INTERVAL_HOURS", 24))

ENABLE_AUTO_SYNC = True
SYNC_HOUR = 3
SYNC_MINUTE = 0

OFFICIAL_CHANNELS = [
    "Metallica",
    "MetallicaTV",
    "MetallicaOfficial",
]

CONCERT_MIN_DURATION = 1800
INTERVIEW_MIN_DURATION = 900
