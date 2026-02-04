from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    youtube_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(500))
    description = Column(Text)
    url = Column(String(500))
    thumbnail_url = Column(String(500))
    duration_seconds = Column(Integer)
    published_at = Column(DateTime)
    view_count = Column(BigInteger)
    content_type = Column(String(20), index=True)
    quality_score = Column(Integer, default=0)
    is_official = Column(Boolean, default=False)
    is_complete = Column(Boolean, default=False)
    tour_name = Column(String(100), index=True)
    venue = Column(String(200))
    date_event = Column(Date, index=True)
    participants = Column(Text)
    quality_tags = Column(Text)
    search_query = Column(String(200))
    channel_id = Column(String(100))
    channel_title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    album = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True)


class SyncStatus(Base):
    __tablename__ = "sync_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_type = Column(String(50))
    last_sync = Column(DateTime)
    videos_added = Column(Integer, default=0)
    status = Column(String(20))
    error_message = Column(Text)


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    query = Column(String(200))
    results_count = Column(Integer)
    searched_at = Column(DateTime, default=datetime.utcnow)


DATABASE_URL = "sqlite+aiosqlite:///./data/metallica.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def init_db_async():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_db():
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.create_task(init_db_async())

    asyncio.run(init_db_async())
