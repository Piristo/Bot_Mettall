import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Video, Tour, SyncStatus, SearchHistory

class VideoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_youtube_id(self, youtube_id: str) -> Optional[Video]:
        result = await self.session.execute(
            select(Video).where(Video.youtube_id == youtube_id)
        )
        return result.scalar_one_or_none()
    
    async def video_exists(self, youtube_id: str) -> bool:
        video = await self.get_by_youtube_id(youtube_id)
        return video is not None
    
    async def add_video(self, video_data: Dict[str, Any]) -> Video:
        video = Video(
            youtube_id=video_data['youtube_id'],
            title=video_data.get('title'),
            description=video_data.get('description'),
            url=video_data.get('url'),
            thumbnail_url=video_data.get('thumbnail_url'),
            duration_seconds=video_data.get('duration_seconds'),
            published_at=video_data.get('published_at'),
            view_count=video_data.get('view_count'),
            content_type=video_data.get('content_type'),
            quality_score=video_data.get('quality_score', 0),
            is_official=video_data.get('is_official', False),
            is_complete=video_data.get('is_complete', False),
            tour_name=video_data.get('tour_name'),
            venue=video_data.get('venue'),
            date_event=video_data.get('date_event'),
            participants=video_data.get('participants'),
            quality_tags=video_data.get('quality_tags'),
            search_query=video_data.get('search_query'),
            channel_id=video_data.get('channel_id'),
            channel_title=video_data.get('channel_title')
        )
        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)
        return video
    
    async def bulk_insert_videos(self, videos_data: List[Dict[str, Any]]) -> int:
        count = 0
        for video_data in videos_data:
            if not await self.video_exists(video_data['youtube_id']):
                await self.add_video(video_data)
                count += 1
        return count
    
    async def get_videos(
        self,
        content_type: Optional[str] = None,
        tour_name: Optional[str] = None,
        year: Optional[int] = None,
        quality_filter: Optional[str] = None,
        sort_by: str = "date_event",
        limit: int = 10,
        offset: int = 0
    ) -> List[Video]:
        query = select(Video)
        
        if content_type:
            query = query.where(Video.content_type == content_type)
        if tour_name:
            query = query.where(Video.tour_name == tour_name)
        if year:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            query = query.where(
                Video.date_event >= start_date,
                Video.date_event <= end_date
            )
        if quality_filter:
            if quality_filter == "HD":
                query = query.where(Video.quality_score >= 60)
            elif quality_filter == "OFFICIAL":
                query = query.where(Video.is_official == True)
            elif quality_filter == "COMPLETE":
                query = query.where(Video.is_complete == True)
        
        if sort_by == "date_event":
            query = query.order_by(Video.date_event.desc())
        elif sort_by == "quality_score":
            query = query.order_by(Video.quality_score.desc())
        elif sort_by == "view_count":
            query = query.order_by(Video.view_count.desc())
        
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_videos_count(
        self,
        content_type: Optional[str] = None,
        tour_name: Optional[str] = None,
        year: Optional[int] = None,
        quality_filter: Optional[str] = None
    ) -> int:
        query = select(func.count(Video.id))
        
        if content_type:
            query = query.where(Video.content_type == content_type)
        if tour_name:
            query = query.where(Video.tour_name == tour_name)
        if year:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            query = query.where(
                Video.date_event >= start_date,
                Video.date_event <= end_date
            )
        if quality_filter:
            if quality_filter == "HD":
                query = query.where(Video.quality_score >= 60)
            elif quality_filter == "OFFICIAL":
                query = query.where(Video.is_official == True)
            elif quality_filter == "COMPLETE":
                query = query.where(Video.is_complete == True)
        
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def get_all_tours(self) -> List[str]:
        result = await self.session.execute(
            select(Video.tour_name).distinct().where(Video.tour_name.isnot(None))
        )
        return [t[0] for t in result.fetchall()]
    
    async def get_available_years(self) -> List[int]:
        result = await self.session.execute(
            select(func.strftime('%Y', Video.date_event))
            .distinct()
            .where(Video.date_event.isnot(None))
            .order_by(func.strftime('%Y', Video.date_event))
        )
        return [int(t[0]) for t in result.fetchall() if t[0]]

class TourRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_name(self, name: str) -> Optional[Tour]:
        result = await self.session.execute(
            select(Tour).where(Tour.name == name)
        )
        return result.scalar_one_or_none()
    
    async def add_tour(self, tour_data: Dict[str, Any]) -> Tour:
        tour = Tour(
            name=tour_data['name'],
            start_date=tour_data.get('start_date'),
            end_date=tour_data.get('end_date'),
            album=tour_data.get('album'),
            description=tour_data.get('description')
        )
        self.session.add(tour)
        await self.session.commit()
        await self.session.refresh(tour)
        return tour

class SyncStatusRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_last_sync(self) -> Optional[SyncStatus]:
        result = await self.session.execute(
            select(SyncStatus).order_by(SyncStatus.id.desc()).limit(1)
        )
        return result.scalar_one_or_none()
    
    async def update_status(self, videos_added: int, status: str = "completed", error: Optional[str] = None):
        sync = SyncStatus(
            sync_type="youtube",
            last_sync=datetime.utcnow(),
            videos_added=videos_added,
            status=status,
            error_message=error
        )
        self.session.add(sync)
        await self.session.commit()

class SearchHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_search(self, user_id: int, query: str, results_count: int):
        search = SearchHistory(
            user_id=user_id,
            query=query,
            results_count=results_count
        )
        self.session.add(search)
        await self.session.commit()
