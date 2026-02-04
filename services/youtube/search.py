from bot.constants import SEARCH_QUERIES, EXCLUDE_KEYWORDS
from services.youtube.api import YouTubeSearch
from services.classifier.content import ContentClassifier
from services.quality.scorer import QualityScorer
from utils.tour_detector import TourDetector
from database.repository import VideoRepository
from database.models import AsyncSessionLocal
import asyncio
import re
from typing import List, Dict, Any

def parse_youtube_duration(duration: str) -> int:
    if not duration:
        return 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds
    return 0

class YouTubeCrawler:
    def __init__(self):
        self.search = YouTubeSearch()
        self.classifier = ContentClassifier()
        self.scorer = QualityScorer()
        self.tour_detector = TourDetector()
    
    async def crawl_all(self) -> List[Dict[str, Any]]:
        all_videos = []
        
        queries = SEARCH_QUERIES.get("concerts", []) + SEARCH_QUERIES.get("interviews", [])
        
        for query in queries:
            print(f"Searching: {query}")
            videos = await self.search.search_concerts(query) if "concert" in query.lower() or "live" in query.lower() else await self.search.search_interviews(query)
            
            for video in videos:
                if self.search.should_exclude(video.get('title', ''), video.get('description', '')):
                    continue
                
                enriched = await self.search.enrich_video_data(video)
                
                content_type = self.classifier.classify(enriched)
                enriched['content_type'] = content_type
                
                quality_score = self.scorer.calculate_score(enriched)
                enriched['quality_score'] = quality_score
                
                is_complete = self.scorer.is_complete(enriched, content_type)
                enriched['is_complete'] = is_complete
                
                quality_tags = self.scorer.get_tags(enriched)
                enriched['quality_tags'] = " • ".join(quality_tags) if quality_tags else ""
                
                tour_name = self.tour_detector.detect_tour(enriched.get('title', ''))
                enriched['tour_name'] = tour_name
                
                enriched['search_query'] = query
                enriched['is_official'] = self.scorer.is_official_channel(enriched.get('channel_title', ''))
                
                all_videos.append(enriched)
            
            await asyncio.sleep(1)
        
        return all_videos
    
    async def crawl_concerts(self) -> List[Dict[str, Any]]:
        return await self._crawl_by_type("concerts")
    
    async def crawl_interviews(self) -> List[Dict[str, Any]]:
        return await self._crawl_by_type("interviews")
    
    async def _crawl_by_type(self, content_type: str) -> List[Dict[str, Any]]:
        all_videos = []
        queries = SEARCH_QUERIES.get(content_type, [])
        
        for query in queries:
            if content_type == "concerts":
                videos = await self.search.search_concerts(query)
            else:
                videos = await self.search.search_interviews(query)
            
            for video in videos:
                if self.search.should_exclude(video.get('title', ''), video.get('description', '')):
                    continue
                
                enriched = await self.search.enrich_video_data(video)
                enriched['content_type'] = content_type
                
                quality_score = self.scorer.calculate_score(enriched)
                enriched['quality_score'] = quality_score
                
                is_complete = self.scorer.is_complete(enriched, content_type)
                enriched['is_complete'] = is_complete
                
                quality_tags = self.scorer.get_tags(enriched)
                enriched['quality_tags'] = " • ".join(quality_tags) if quality_tags else ""
                
                tour_name = self.tour_detector.detect_tour(enriched.get('title', ''))
                enriched['tour_name'] = tour_name
                
                enriched['search_query'] = query
                enriched['is_official'] = self.scorer.is_official_channel(enriched.get('channel_title', ''))
                
                all_videos.append(enriched)
            
            await asyncio.sleep(1)
        
        return all_videos
    
    async def sync_to_database(self) -> int:
        videos = await self.crawl_all()
        
        async with AsyncSessionLocal() as session:
            repo = VideoRepository(session)
            count = await repo.bulk_insert_videos(videos)
            return count
    
    async def enrich_video_data(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        video_ids = [video_data['youtube_id']]
        details = await self.search.api.get_video_details(video_ids)
        
        if details:
            detail = details[0]
            video_data.update({
                'duration': detail.get('duration'),
                'view_count': detail.get('view_count'),
                'duration_seconds': parse_youtube_duration(detail.get('duration', ''))
            })
        
        return video_data
