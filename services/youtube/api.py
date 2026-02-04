from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bot.config import YOUTUBE_API_KEY
from bot.constants import EXCLUDE_KEYWORDS
import asyncio
from typing import Dict, List, Optional, Any

class YouTubeAPI:
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.youtube = None
    
    async def get_client(self):
        if self.youtube is None:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._init_client)
        return self.youtube
    
    def _init_client(self):
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 50,
        order: str = "relevance"
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.youtube.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    maxResults=max_results,
                    order=order,
                    videoDuration="long"
                ).execute()
            )
            
            videos = []
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                video_data = {
                    "youtube_id": video_id,
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"] if "high" in item["snippet"]["thumbnails"] else item["snippet"]["thumbnails"]["default"]["url"],
                    "channel_title": item["snippet"]["channelTitle"],
                    "channel_id": item["snippet"]["channelId"],
                    "published_at": item["snippet"]["publishedAt"],
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                }
                videos.append(video_data)
            
            return videos
        
        except HttpError as e:
            print(f"YouTube API Error: {e}")
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        if not video_ids or not self.api_key:
            return []
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=",".join(video_ids)
                ).execute()
            )
            
            videos = []
            for item in response.get("items", []):
                video_data = {
                    "youtube_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"] if "high" in item["snippet"]["thumbnails"] else "",
                    "channel_id": item["snippet"]["channelId"],
                    "channel_title": item["snippet"]["channelTitle"],
                    "published_at": item["snippet"]["publishedAt"],
                    "duration": item["contentDetails"]["duration"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "url": f"https://www.youtube.com/watch?v={item['id']}"
                }
                videos.append(video_data)
            
            return videos
        
        except HttpError as e:
            print(f"YouTube API Error: {e}")
            return []
        except Exception as e:
            print(f"Details error: {e}")
            return []

class YouTubeSearch:
    def __init__(self):
        self.api = YouTubeAPI()
    
    async def search_concerts(self, query: str) -> List[Dict[str, Any]]:
        search_query = f"Metallica {query} concert live full show"
        return await self.api.search_videos(search_query)
    
    async def search_interviews(self, query: str) -> List[Dict[str, Any]]:
        search_query = f"Metallica {query} interview full"
        return await self.api.search_videos(search_query)
    
    def should_exclude(self, title: str, description: str = "") -> bool:
        text = f"{title} {description}".lower()
        for keyword in EXCLUDE_KEYWORDS:
            if keyword.lower() in text:
                return True
        return False
    
    async def enrich_video_data(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        video_ids = [video_data['youtube_id']]
        details = await self.api.get_video_details(video_ids)
        
        if details:
            detail = details[0]
            video_data.update({
                'duration': detail.get('duration'),
                'view_count': detail.get('view_count'),
                'duration_seconds': self._parse_duration(detail.get('duration', ''))
            })
        
        return video_data
    
    def _parse_duration(self, duration: str) -> int:
        import re
        if not duration:
            return 0
        
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        return 0
