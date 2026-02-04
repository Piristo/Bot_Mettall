from datetime import datetime, date
from typing import Optional
import re

class DateParser:
    @staticmethod
    def parse_youtube_date(date_string: str) -> Optional[date]:
        if not date_string:
            return None
        
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.date()
        except Exception:
            return None
    
    @staticmethod
    def extract_year(title: str) -> Optional[int]:
        if not title:
            return None
        
        year_match = re.search(r'(19[8-9]\d|20[0-2]\d)', title)
        if year_match:
            return int(year_match.group(1))
        return None
    
    @staticmethod
    def extract_date_from_title(title: str) -> Optional[date]:
        if not title:
            return None
        
        year = DateParser.extract_year(title)
        if year:
            return date(year, 1, 1)
        return None
    
    @staticmethod
    def format_date(date_obj: Optional[date], format: str = "%Y-%m-%d") -> str:
        if not date_obj:
            return "Unknown"
        return date_obj.strftime(format)
    
    @staticmethod
    def parse_duration(duration: str) -> int:
        if not duration:
            return 0
        
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        return 0
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        if not seconds:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
