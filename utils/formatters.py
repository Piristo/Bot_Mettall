from database.models import Video
from utils.date_parser import DateParser

class Formatter:
    @staticmethod
    def format_video_card(video: Video) -> str:
        title = video.title or "Unknown Title"
        date_str = DateParser.format_date(video.date_event)
        duration_str = DateParser.format_duration(video.duration_seconds or 0)
        url = video.url or f"https://www.youtube.com/watch?v={video.youtube_id}"
        quality_tags = video.quality_tags or ""
        tour_name = video.tour_name or "Unknown Tour"
        venue = video.venue or "Unknown Venue"
        
        lines = [
            f"🎸 {date_str} - {title}",
            f"📍 {venue}",
            f"⏱️ {duration_str}",
            f"📺 {url}",
        ]
        
        if quality_tags:
            lines.append(f"⭐️ {quality_tags}")
        
        lines.append(f"🎵 {tour_name}")
        lines.append("")
        lines.append(f"🔗 {url}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_video_short(video: Video) -> str:
        title = video.title or "Unknown"
        date_str = DateParser.format_date(video.date_event)
        duration_str = DateParser.format_duration(video.duration_seconds or 0)
        
        return f"🎸 {date_str} | {duration_str} | {title}"
    
    @staticmethod
    def format_stats(concert_count: int, interview_count: int, total_count: int) -> str:
        return (
            f"📊 Статистика базы:\n"
            f"🎸 Концертов: {concert_count}\n"
            f"🎤 Интервью: {interview_count}\n"
            f"📦 Всего: {total_count}"
        )
    
    @staticmethod
    def format_tour_header(tour_name: str, count: int) -> str:
        return (
            f"╔══════════════════════════════════════════╗\n"
            f"🎸 {tour_name}\n"
            f"╠══════════════════════════════════════════╣\n"
            f"📊 Найдено: {count} записей\n"
            f"╠══════════════════════════════════════════╣\n"
        )
    
    @staticmethod
    def format_search_results_header(query: str, count: int, content_type: str) -> str:
        type_label = "концертов" if content_type == "concert" else "интервью"
        return f"🔍 По запросу \"{query}\" найдено {count} {type_label}"
    
    @staticmethod
    def format_error(message: str) -> str:
        return f"❌ Ошибка: {message}"
    
    @staticmethod
    def format_success(message: str) -> str:
        return f"✅ {message}"
    
    @staticmethod
    def format_no_results(content_type: str) -> str:
        if content_type == "concert":
            return "😔 Концерты не найдены. Попробуйте обновить базу (/refresh)"
        elif content_type == "interview":
            return "😔 Интервью не найдены. Попробуйте обновить базу (/refresh)"
        else:
            return "😔 Записи не найдены. Попробуйте обновить базу (/refresh)"
    
    @staticmethod
    def format_refresh_status(videos_found: int, videos_added: int) -> str:
        return (
            f"🔄 Обновление завершено!\n"
            f"📊 Найдено: {videos_found}\n"
            f"➕ Добавлено: {videos_added}"
        )
