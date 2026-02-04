import json
from pathlib import Path
from typing import Optional, Dict, Any

class TourDetector:
    def __init__(self):
        self.tours = self._load_tours()
    
    def _load_tours(self) -> list:
        tours_file = Path(__file__).parent.parent.parent / "data" / "tours.json"
        if tours_file.exists():
            with open(tours_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("tours", [])
        return []
    
    def detect_tour(self, title: str) -> Optional[str]:
        if not title:
            return None
        
        title_lower = title.lower()
        
        tour_keywords = {
            "kill 'em all": ["kill 'em all", "kill em all", "kill 'em", "kill em"],
            "ride the lightning": ["ride the lightning", "ride lightning"],
            "master of puppets": ["master of puppets", "mop tour"],
            "...and justice for all": ["and justice for all", "ajfa tour", "justice tour"],
            "black album": ["black album", "self-named album", "metallica album"],
            "load": ["load tour", "load era"],
            "reload": ["reload tour", "reload era"],
            "garage inc": ["garage inc", "garage inc."],
            "st. anger": ["st. anger", "st anger", "anger tour"],
            "death magnetic": ["death magnetic", "magnetic tour"],
            "hardwired": ["hardwired", "hardwired to self-destruct", "hardwired tour"],
            "s&m": ["s&m", "s & m", "symphony", "orchestra"],
            "m72": ["m72", "m 72", "72 tour", "no repeat weekends"],
            "worldwired": ["worldwired", "world wired", "worldwired tour"],
            "world magnetic": ["world magnetic", "magnetic world tour"],
            "summer tour": ["summer tour", "european tour"],
            "escape from the studio": ["escape from the studio", "studio escape"]
        }
        
        for tour_name, keywords in tour_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return self._get_tour_display_name(tour_name)
        
        year_match = self._extract_year(title_lower)
        if year_match:
            tour = self._find_tour_by_year(year_match)
            if tour:
                return tour
        
        return None
    
    def _get_tour_display_name(self, tour_key: str) -> str:
        display_names = {
            "kill 'em all": "Kill 'Em All Tour",
            "ride the lightning": "Ride the Lightning Tour",
            "master of puppets": "Master of Puppets Tour",
            "...and justice for all": "...And Justice for All Tour",
            "black album": "Black Album Tour",
            "load": "Load Tour",
            "reload": "ReLoad Tour",
            "garage inc": "Garage Inc. Tour",
            "st. anger": "St. Anger Tour",
            "death magnetic": "Death Magnetic Tour",
            "hardwired": "Hardwired... to Self-Destruct Tour",
            "s&m": "S&M Tour",
            "m72": "M72 World Tour",
            "worldwired": "WorldWired Tour",
            "world magnetic": "World Magnetic Tour",
            "summer tour": "Summer Tour",
            "escape from the studio": "Escape from the Studio Tour"
        }
        return display_names.get(tour_key, tour_key.title())
    
    def _extract_year(self, title: str) -> Optional[int]:
        import re
        year_match = re.search(r'(19[8-9]\d|20[0-2]\d)', title)
        if year_match:
            return int(year_match.group(1))
        return None
    
    def _find_tour_by_year(self, year: int) -> Optional[str]:
        for tour in self.tours:
            start_year = int(tour.get("start_date", "0000-00-00")[:4])
            end_year = int(tour.get("end_date", "0000-00-00")[:4])
            if start_year <= year <= end_year:
                return tour.get("name")
        return None
    
    def get_all_tours(self) -> list:
        return [tour.get("name") for tour in self.tours]
    
    def get_tour_info(self, tour_name: str) -> Optional[Dict]:
        for tour in self.tours:
            if tour.get("name") == tour_name:
                return tour
        return None
