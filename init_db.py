#!/usr/bin/env python3
"""
Скрипт инициализации базы данных Metallica Archive Bot
"""
import sys
import json
from pathlib import Path
from datetime import datetime

def init_database():
    """Инициализация базы данных"""
    print("📦 Инициализация базы данных...")
    
    try:
        from database.models import init_db, engine, Base
        from database.repository import TourRepository
        from database.models import AsyncSessionLocal
        
        init_db()
        print("✅ База данных создана")
        
        load_tours()
        load_keywords()
        
        print("\n🎉 Инициализация завершена!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Пожалуйста, установите зависимости: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def load_tours():
    """Загрузка туров из JSON"""
    print("\n🎸 Загрузка туров Metallica...")
    
    tours_file = Path(__file__).parent.parent / "data" / "tours.json"
    
    if not tours_file.exists():
        print("⚠️ Файл tours.json не найден")
        return
    
    with open(tours_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tours = data.get('tours', [])
    print(f"📊 Найдено {len(tours)} туров")
    
    for tour in tours:
        print(f"  - {tour['name']} ({tour['start_date']} - {tour['end_date']})")

def load_keywords():
    """Загрузка ключевых слов"""
    print("\n🔑 Загрузка ключевых слов...")
    
    keywords_file = Path(__file__).parent.parent / "data" / "keywords.json"
    
    if not keywords_file.exists():
        print("⚠️ Файл keywords.json не найден")
        return
    
    with open(keywords_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    concerts = data.get('concerts', {}).get('keywords', [])
    interviews = data.get('interviews', {}).get('keywords', [])
    
    print(f"📊 Ключевых слов для концертов: {len(concerts)}")
    print(f"📊 Ключевых слов для интервью: {len(interviews)}")

def show_stats():
    """Показать статистику базы"""
    print("\n📊 Статистика...")
    
    data_dir = Path(__file__).parent.parent / "data"
    db_file = data_dir / "metallica.db"
    
    if db_file.exists():
        size = db_file.stat().st_size
        print(f"📦 Размер базы данных: {size:,} байт")
    else:
        print("📦 База данных еще не создана")

def main():
    """Главная функция"""
    print("=" * 50)
    print("🎸 Metallica Archive Bot - Инициализация БД")
    print("=" * 50)
    print()
    
    action = sys.argv[1] if len(sys.argv) > 1 else "init"
    
    if action == "init":
        init_database()
        show_stats()
    elif action == "stats":
        show_stats()
    elif action == "tours":
        load_tours()
    elif action == "keywords":
        load_keywords()
    else:
        print("Использование:")
        print("  python init_db.py init    - Инициализировать БД")
        print("  python init_db.py stats   - Показать статистику")
        print("  python init_db.py tours   - Показать туры")
        print("  python init_db.py keywords - Показать ключевые слова")

if __name__ == "__main__":
    main()
