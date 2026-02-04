import telebot
import threading
from telebot import types
import sqlite3
import json
import requests
import time
import os

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

bot = telebot.TeleBot(TOKEN)

DATABASE = "data/metallica.db"

INVIDIOUS_INSTANCES = [
    "yewtu.be",
    "invidious.snopyta.org",
    "invidious.kavin.rocks",
]

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY,
                  youtube_id TEXT UNIQUE,
                  title TEXT,
                  url TEXT,
                  content_type TEXT,
                  tour_name TEXT,
                  venue TEXT,
                  duration_seconds INTEGER,
                  quality_tags TEXT,
                  date_event TEXT)''')
    conn.commit()
    conn.close()

def get_concerts():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE content_type='concert' ORDER BY date_event DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows

def get_interviews():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE content_type='interview' ORDER BY date_event DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows

def search_youtube(query, max_results=10):
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"https://{instance}/api/v1/search"
            params = {"q": query, "type": "video", "max_results": max_results}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                videos = []
                for item in data:
                    if item.get("type") == "video":
                        duration = item.get("lengthSeconds", 0)
                        title = item.get("title", "")
                        
                        content_type = "concert"
                        keywords_concert = ["concert", "live", "performance", "show", "tour"]
                        keywords_interview = ["interview", "talk", "conversation"]
                        
                        if any(kw in title.lower() for kw in keywords_interview):
                            content_type = "interview"
                        elif any(kw in title.lower() for kw in keywords_concert):
                            content_type = "concert"
                        
                        tour_name = detect_tour(title)
                        
                        videos.append({
                            "youtube_id": item.get("videoId"),
                            "title": title,
                            "url": f"https://www.youtube.com/watch?v={item.get('videoId')}",
                            "content_type": content_type,
                            "tour_name": tour_name,
                            "duration_seconds": duration,
                            "quality_tags": "HD" if duration > 1800 else ""
                        })
                return videos
        except:
            continue
    return []

def detect_tour(title):
    title_lower = title.lower()
    tours = {
        "m72": ["m72", "72 tour"],
        "worldwired": ["worldwired", "world wired"],
        "world magnetic": ["world magnetic", "death magnetic"],
        "black album": ["black album"],
        "hardwired": ["hardwired"],
        "st anger": ["st anger", "st. anger"],
        "load": ["load"],
        "reload": ["reload"],
        "garage inc": ["garage inc"],
        "justice": ["justice", "and justice"],
        "master of puppets": ["master of puppets", "puppets"],
        "ride the lightning": ["ride the lightning", "lightning"],
        "kill em all": ["kill 'em all", "kill em all"],
    }
    for tour, keywords in tours.items():
        for kw in keywords:
            if kw in title_lower:
                return tour.title()
    return None

def save_video_to_db(video):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('''INSERT OR IGNORE INTO videos 
                     (youtube_id, title, url, content_type, tour_name, duration_seconds, quality_tags)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (video['youtube_id'], video['title'], video['url'], 
                    video['content_type'], video.get('tour_name'), 
                    video.get('duration_seconds', 0), video.get('quality_tags', '')))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def format_video_row(row):
    duration = row[7] if row[7] else 0
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    return f"""🎸 *{row[2]}*
📍 {row[6] if row[6] else 'Unknown'}
⏱️ {hours}:{minutes:02d}
🔗 [Смотреть]({row[3]})
⭐️ {row[8] if row[8] else 'HD'}
━━━━━━━━━━━━━━━━━━"""

def format_video(video):
    duration = video.get('duration_seconds', 0)
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    return f"""🎸 *{video['title']}*
🔗 [Смотреть]({video['url']})
⏱️ {hours}:{minutes:02d}
🏷️ {video.get('tour_name', 'Metallica')}
⭐️ {video.get('quality_tags', 'HD')}
━━━━━━━━━━━━━━━━━━"""

@bot.message_handler(commands=['start'])
def start(message):
    text = """🎸 *Metallica Archive Bot*

Добро пожаловать! Бот ищет концерты и интервью Metallica.

Команды:
/search [запрос] - Поиск видео
/concerts - Концерты из базы
/interviews - Интервью из базы
/help - Помощь"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help(message):
    text = """🎸 *Команды:*

/search [запрос] - Поиск концертов и интервью
/concerts - Концерты из базы
/interviews - Интервью из базы
/archive - Весь архив
/stats - Статистика

Пример: /search Metallica Live 2024"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['search'])
def search(message):
    query = message.text.replace('/search', '').strip()
    if not query:
        bot.send_message(message.chat.id, "Введите запрос: /search [текст]\nНапример: /search Metallica Live 2024")
        return
    
    bot.send_message(message.chat.id, f"🔍 Ищу: {query}...")
    
    videos = search_youtube(f"Metallica {query}")
    
    if videos:
        text = f"🎸 *Найдено {len(videos)} видео:*\n\n"
        for i, video in enumerate(videos[:10], 1):
            text += f"{i}. {format_video(video)}\n"
        
        if len(videos) > 10:
            text += f"\n... и ещё {len(videos) - 10} видео"
        
        bot.send_message(message.chat.id, text, parse_mode='Markdown', disable_web_page_preview=True)
        
        save_all = input("Сохранить в базу? (y/n): ")
        if save_all.lower() == 'y':
            for video in videos:
                save_video_to_db(video)
            bot.send_message(message.chat.id, "✅ Сохранено в базу!")
    else:
        bot.send_message(message.chat.id, "😔 Видео не найдено. Попробуйте другой запрос.")

@bot.message_handler(commands=['concerts'])
def concerts(message):
    videos = get_concerts()
    if videos:
        text = "🎸 *Концерты Metallica*\n\n"
        for row in videos:
            text += format_video_row(row) + "\n"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, """😔 Концерты не найдены.

Используйте /search для поиска:
/search Metallica full concert
/search Metallica live show""")

@bot.message_handler(commands=['interviews'])
def interviews(message):
    videos = get_interviews()
    if videos:
        text = "🎤 *Интервью Metallica*\n\n"
        for row in videos:
            text += format_video_row(row) + "\n"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, """😔 Интервью не найдены.

Используйте /search для поиска:
/search Metallica interview
/search James Hetfield interview""")

@bot.message_handler(commands=['archive'])
def archive(message):
    concerts = get_concerts()
    interviews = get_interviews()
    text = f"""📦 *Архив Metallica*

🎸 Концертов: {len(concerts)}
🎤 Интервью: {len(interviews)}
📦 Всего: {len(concerts) + len(interviews)}

Используйте /search для поиска новых видео!"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def stats(message):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM videos WHERE content_type='concert'")
    concerts = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM videos WHERE content_type='interview'")
    interviews = c.fetchone()[0]
    conn.close()
    text = f"""📊 *Статистика*

🎸 Концертов: {concerts}
🎤 Интервью: {interviews}
📦 Всего: {concerts + interviews}

/search [запрос] - Поиск новых видео"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def echo(message):
    if message.text and not message.text.startswith('/'):
        bot.send_message(message.chat.id, "Используйте /search для поиска\nНапример: /search Metallica Live 2024")
    else:
        bot.send_message(message.chat.id, "Неизвестная команда. /help")

if __name__ == "__main__":
    init_db()
    print("🎸 Metallica Archive Bot запущен!")
    bot.infinity_polling()
