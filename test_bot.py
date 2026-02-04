#!/usr/bin/env python3
"""
Тестовый скрипт для проверки модулей Metallica Archive Bot
"""

import sys
import asyncio
from pathlib import Path

def test_imports():
    """Проверка импортов модулей"""
    print("🔍 Проверка импортов...")
    
    try:
        from bot.config import TELEGRAM_BOT_TOKEN, YOUTUBE_API_KEY
        print("✅ bot.config - OK")
    except ImportError as e:
        print(f"❌ bot.config - ОШИБКА: {e}")
        return False
    
    try:
        from bot.constants import SEARCH_QUERIES, EXCLUDE_KEYWORDS
        print("✅ bot.constants - OK")
    except ImportError as e:
        print(f"❌ bot.constants - ОШИБКА: {e}")
        return False
    
    try:
        from utils.date_parser import DateParser
        print("✅ utils.date_parser - OK")
    except ImportError as e:
        print(f"❌ utils.date_parser - ОШИБКА: {e}")
        return False
    
    try:
        from utils.tour_detector import TourDetector
        print("✅ utils.tour_detector - OK")
    except ImportError as e:
        print(f"❌ utils.tour_detector - ОШИБКА: {e}")
        return False
    
    try:
        from utils.formatters import Formatter
        print("✅ utils.formatters - OK")
    except ImportError as e:
        print(f"❌ utils.formatters - ОШИБКА: {e}")
        return False
    
    return True

def test_date_parser():
    """Проверка парсера дат"""
    print("\n🔍 Проверка DateParser...")
    
    try:
        from utils.date_parser import DateParser
        
        # Тест формата длительности
        duration = DateParser.parse_duration("PT2H45M30S")
        assert duration == 9930, f"Ожидалось 9930, получено {duration}"
        
        formatted = DateParser.format_duration(9930)
        assert formatted == "2:45:30", f"Ожидалось '2:45:30', получено '{formatted}'"
        
        # Тест извлечения года
        year = DateParser.extract_year("Metallica Live 2024 Madison Square Garden")
        assert year == 2024, f"Ожидалось 2024, получено {year}"
        
        print("✅ DateParser - OK")
        return True
    except Exception as e:
        print(f"❌ DateParser - ОШИБКА: {e}")
        return False

def test_tour_detector():
    """Проверка детектора туров"""
    print("\n🔍 Проверка TourDetector...")
    
    try:
        from utils.tour_detector import TourDetector
        
        detector = TourDetector()
        
        # Тест определения тура
        tour = detector.detect_tour("Metallica M72 World Tour 2024")
        assert tour == "M72 World Tour", f"Ожидалось 'M72 World Tour', получено '{tour}'"
        
        tour = detector.detect_tour("Metallica Black Album 1991")
        assert tour == "Black Album Tour", f"Ожидалось 'Black Album Tour', получено '{tour}'"
        
        tour = detector.detect_tour("Metallica Live 2019")
        assert tour is not None, "Тур не должен быть None"
        
        print("✅ TourDetector - OK")
        return True
    except Exception as e:
        print(f"❌ TourDetector - ОШИБКА: {e}")
        return False

def test_quality_scorer():
    """Проверки оценки качества"""
    print("\n🔍 Проверка QualityScorer...")
    
    try:
        from services.quality.scorer import QualityScorer
        
        scorer = QualityScorer()
        
        # Тест официального канала
        is_official = scorer.is_official_channel("Metallica TV")
        assert is_official == True, "Должен быть официальным каналом"
        
        is_not_official = scorer.is_official_channel("Some Fan Channel")
        assert is_not_official == False, "Не должен быть официальным каналом"
        
        # Тест полноты записи
        video_concert = {
            'title': 'Metallica Full Concert',
            'duration_seconds': 5400  # 1.5 часа
        }
        is_complete = scorer.is_complete(video_concert, 'concert')
        assert is_complete == True, "Должен быть полным концертом"
        
        video_short = {
            'title': 'Metallica Clip',
            'duration_seconds': 300  # 5 минут
        }
        is_complete = scorer.is_complete(video_short, 'concert')
        assert is_complete == False, "Не должен быть полным концертом"
        
        print("✅ QualityScorer - OK")
        return True
    except Exception as e:
        print(f"❌ QualityScorer - ОШИБКА: {e}")
        return False

def test_classifier():
    """Проверка классификатора"""
    print("\n🔍 Проверка ContentClassifier...")
    
    try:
        from services.classifier.content import ContentClassifier
        
        classifier = ContentClassifier()
        
        # Тест концерта
        video_concert = {
            'title': 'Metallica Live at Wembley Stadium 2024 Full Concert',
            'description': 'Complete live performance'
        }
        content_type = classifier.classify(video_concert)
        assert content_type == 'concert', f"Ожидалось 'concert', получено '{content_type}'"
        
        # Тест интервью
        video_interview = {
            'title': 'James Hetfield Exclusive Interview 2024',
            'description': 'Full conversation with Metallica lead singer'
        }
        content_type = classifier.classify(video_interview)
        assert content_type == 'interview', f"Ожидалось 'interview', получено '{content_type}'"
        
        print("✅ ContentClassifier - OK")
        return True
    except Exception as e:
        print(f"❌ ContentClassifier - ОШИБКА: {e}")
        return False

def test_formatters():
    """Проверка форматтеров"""
    print("\n🔍 Проверка Formatters...")
    
    try:
        from utils.formatters import Formatter
        from datetime import date
        
        # Тест форматирования статистики
        stats = Formatter.format_stats(100, 50, 150)
        assert "100" in stats, "Должно содержать количество концертов"
        assert "50" in stats, "Должно содержать количество интервью"
        
        # Тест ошибки
        error = Formatter.format_error("Test error")
        assert "Test error" in error, "Должно содержать текст ошибки"
        
        # Тест успеха
        success = Formatter.format_success("Test success")
        assert "Test success" in success, "Должно содержать текст успеха"
        
        print("✅ Formatters - OK")
        return True
    except Exception as e:
        print(f"❌ Formatters - ОШИБКА: {e}")
        return False

def test_files():
    """Проверка наличия файлов"""
    print("\n🔍 Проверка файлов...")
    
    required_files = [
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        ".env.example",
        "bot/main.py",
        "bot/config.py",
        "bot/constants.py",
        "database/models.py",
        "database/repository.py",
        "services/youtube/api.py",
        "services/youtube/search.py",
        "services/classifier/content.py",
        "services/quality/scorer.py",
        "utils/tour_detector.py",
        "utils/date_parser.py",
        "utils/formatters.py",
        "data/tours.json",
        "data/keywords.json"
    ]
    
    all_ok = True
    for file_path in required_files:
        path = Path(__file__).parent.parent / file_path
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")
            all_ok = False
    
    return all_ok

def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("🎸 Metallica Archive Bot - Тестирование")
    print("=" * 60)
    
    results = []
    
    results.append(("Импорты", test_imports()))
    results.append(("Файлы", test_files()))
    results.append(("DateParser", test_date_parser()))
    results.append(("TourDetector", test_tour_detector()))
    results.append(("QualityScorer", test_quality_scorer()))
    results.append(("ContentClassifier", test_classifier()))
    results.append(("Formatters", test_formatters()))
    
    print("\n" + "=" * 60)
    print("📊 Результаты тестирования:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"📈 Всего: {passed + failed} | ✅ {passed} | ❌ {failed}")
    
    if failed == 0:
        print("\n🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print(f"\n⚠️ {failed} тест(ов) провалено(о)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
