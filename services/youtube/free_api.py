from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import re

class FreeYouTubeAPI:
    INVIDIOUS_INSTANCES = [
        "yewtu.be",
        "invidious.snopyta.org",
        "invidious.kavin.rocks",
    ]
    
    def __init__(self):
        self.current_instance = 0
    
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        instance = self.INVIDIOUS_INSTANCES[self.current_instance]
        url = f"https://{instance}/api/v1/search"
        
        params = {
            "q": query,
            "type": "video",
            "max_results": max_results
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results(data)
                    else:
                        self.current_instance = (self.current_instance + 1) % len(self.INVIDIOUS_INSTANCES)
                        return []
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def _parse_results(self, data: List) -> List[Dict]:
        videos = []
        for item in data:
            if item.get("type") == "video":
                video = {
                    "youtube_id": item.get("videoId"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "thumbnail_url": item.get("thumbnail"),
                    "channel_title": item.get("author"),
                    "channel_id": item.get("authorId"),
                    "published_at": item.get("published"),
                    "url": f"https://www.youtube.com/watch?v={item.get('videoId')}",
                    "view_count": item.get("viewCount"),
                    "length_seconds": item.get("lengthSeconds")
                }
                videos.append(video)
        return videos

async def test():
    api = FreeYouTubeAPI()
    results = await api.search_videos("Metallica full concert", 5)
    for video in results:
        print(f"- {video['title']}")
        print(f"  https://youtube.com/watch?v={video['youtube_id']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
