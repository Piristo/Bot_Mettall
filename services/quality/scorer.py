from typing import Dict, Any
from bot.config import CONCERT_MIN_DURATION, INTERVIEW_MIN_DURATION
from bot.constants import QUALITY_INDICATORS

class QualityScorer:
    OFFICIAL_CHANNELS = [
        "metallica", "metallicatv", "metallicaofficial",
        "metallica tv", "metallica official"
    ]
    
    def calculate_score(self, video_data: Dict[str, Any]) -> int:
        score = 0
        title = video_data.get('title', '').lower()
        channel_title = video_data.get('channel_title', '').lower()
        duration = video_data.get('duration_seconds', 0)
        view_count = video_data.get('view_count', 0)
        
        if self.is_official_channel(channel_title):
            score += 40
        
        for indicator in QUALITY_INDICATORS.get("hd", []):
            if indicator in title:
                score += 20
                break
        
        if any(indicator in title for indicator in QUALITY_INDICATORS.get("complete", [])):
            score += 15
        
        if duration > 3600:
            score += 10
        elif duration > 2700:
            score += 7
        elif duration > 1800:
            score += 5
        
        if view_count > 1000000:
            score += 15
        elif view_count > 100000:
            score += 10
        elif view_count > 10000:
            score += 5
        
        return min(score, 100)
    
    def is_official_channel(self, channel_title: str) -> bool:
        if not channel_title:
            return False
        channel_lower = channel_title.lower()
        return any(official in channel_lower for official in self.OFFICIAL_CHANNELS)
    
    def is_complete(self, video_data: Dict[str, Any], content_type: str) -> bool:
        title = video_data.get('title', '').lower()
        duration = video_data.get('duration_seconds', 0)
        
        import re
        if re.search(r'part\s*\d+', title):
            return False
        
        if content_type == "concert":
            return duration >= CONCERT_MIN_DURATION
        else:
            return duration >= INTERVIEW_MIN_DURATION
    
    def get_tags(self, video_data: Dict[str, Any]) -> list:
        tags = []
        title = video_data.get('title', '').lower()
        channel_title = video_data.get('channel_title', '')
        quality_score = video_data.get('quality_score', 0)
        is_complete = video_data.get('is_complete', False)
        
        if self.is_official_channel(channel_title):
            tags.append("OFFICIAL")
        
        if quality_score >= 60 or any(hd in title for hd in ["720p", "1080p", "hd"]):
            tags.append("HD")
        
        if is_complete:
            tags.append("COMPLETE")
        
        return tags
    
    def get_quality_filter(self, quality_score: int) -> str:
        if quality_score >= 80:
            return "HD"
        elif quality_score >= 50:
            return "SD"
        else:
            return "LQ"
