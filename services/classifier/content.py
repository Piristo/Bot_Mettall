from typing import Dict, Any
from bot.constants import SEARCH_QUERIES

class ContentClassifier:
    CONCERT_KEYWORDS = [
        "concert", "live", "performance", "show", "tour",
        "stadium", "arena", "live at", "in concert",
        "world tour", "live show", "full show"
    ]
    
    INTERVIEW_KEYWORDS = [
        "interview", "talk", "conversation", "chat",
        "q&a", "question and answer", "in-depth",
        "exclusive", "full interview", "complete interview",
        "sitting down", "one on one", "press conference"
    ]
    
    def classify(self, video_data: Dict[str, Any]) -> str:
        title = video_data.get('title', '').lower()
        description = video_data.get('description', '').lower()
        text = f"{title} {description}"
        
        concert_score = sum(1 for kw in self.CONCERT_KEYWORDS if kw in text)
        interview_score = sum(1 for kw in self.INTERVIEW_KEYWORDS if kw in text)
        
        if interview_score > concert_score:
            return "interview"
        elif concert_score > interview_score:
            return "concert"
        else:
            return self._fallback_classify(video_data)
    
    def _fallback_classify(self, video_data: Dict[str, Any]) -> str:
        channel_title = video_data.get('channel_title', '').lower()
        duration = video_data.get('duration_seconds', 0)
        
        if "interview" in channel_title:
            return "interview"
        if "live" in channel_title or "concert" in channel_title:
            return "concert"
        if duration > 3600:
            return "concert"
        if duration > 1800:
            return "concert"
        
        return "concert"
