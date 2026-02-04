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
    "invidious.tube",
    "invidious.jingl.xyz",
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
    print(f"Searching for: {query}")
    
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"https://{instance}/api/v1/search"
            params = {"q": query, "type": "video", "max_results": max_results}
            print(f"Trying: {instance}")
            
            response = requests.get(url, params=params, timeout=15)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data)} results")
                
                videos = []
                for item in data:
                    if item.get("type") == "video":
                        duration = item.get("lengthSeconds", 0)
                        title = item.get("title", "")
                        
                        content_type = "concert"
                        keywords_interview = ["interview", "talk", "conversation", "q&a", "press conference"]
                        
                        if any(kw in title.lower() for kw in keywords_interview):
                            content_type = "interview"
                        
                        tour_name = detect_tour(title)
                        
                        videos.append({
                            "youtube_id": item.get("videoId"),
                            "title": title,
                            "url": f"https://www.youtube.com/watch?v={item.get('videoId')}",
                            "content_type": content_type,
                            "tour_name": tour_name,
                            "duration_seconds": duration,
                            "quality_tags": "HD" if duration > 1800 else "SD"
                        })
                
                if videos:
                    return videos
                    
        except Exception as e:
            print(f"Error with {instance}: {e}")
            continue
    
    return []

def search_youtube_fallback(query):
    print(f"Fallback search for: {query}")
    
    search_queries = [
        f"Metallica {query} full concert",
        f"Metallica {query} live",
        f"Metallica {query} performance"
    ]
    
    for sq in search_queries:
        videos = search_youtube(sq, 5)
        if videos:
            return videos
    
    return []

def detect_tour(title):
    title_lower = title.lower()
    tours = {
        "M72 World Tour": ["m72", "72 tour", "no repeat"],
        "WorldWired Tour": ["worldwired", "world wired", "hardwired to self-destruct"],
        "World Magnetic Tour": ["world magnetic", "death magnetic"],
        "Black Album Tour": ["black album", "self-titled"],
        "St. Anger Tour": ["st anger", "st. anger"],
        "Load Tour": ["load tour", "load era"],
        "ReLoad Tour": ["reload tour", "reload era"],
        "Garage Inc. Tour": ["garage inc"],
        "Justice Tour": ["and justice for all", "justice tour"],
        "Master of Puppets Tour": ["master of puppets", "puppets tour"],
        "Ride the Lightning Tour": ["ride the lightning", "lightning tour"],
        "Kill 'Em All Tour": ["kill 'em all", "kill em all"],
    }
    
    for tour, keywords in tours.items():
        for kw in keywords:
            if kw in title_lower:
                return tour
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
    except Exception as e:
        print(f"Save error: {e}")
        return False
    finally:
        conn.close()

def format_video(video):
    duration = video.get('duration_seconds', 0)
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    
    tour = video.get('tour_name', 'Metallica')
    quality = video.get('quality_tags', 'HD')
    
    return f"""🎸 *{video['title']}*
⏱️ {hours}:{minutes:02d} | 🏷️ {tour} | {quality}
🔗 [Смотреть]({video['url']})"""

@bot.message_handler(commands=['start'])
def start(message):
    text = """🎸 *Metallica Archive Bot*

Бот для поиска концертов и интервью Metallica!

Команды:
/search [запрос] - Поиск видео
/concerts - Концерты
/interviews - Интервью
/help - Помощь"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help(message):
    text = """🎸 *Команды:*

/search [запрос] - Поиск
/concerts - Из базы
/interviews - Из базы
/archive - Архив
/stats - Статистика

Примеры:
/search Metallica Live 2024
/search interview Lars Ulrich
/search M72 World Tour"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['search'])
def search(message):
    query = message.text.replace('/search', '').strip()
    if not query:
        bot.send_message(message.chat.id, "Введите: /search [запрос]\nПример: /search Metallica Live 2024")
        return
    
    bot.send_message(message.chat.id, f"🔍 Ищу: *{query}*...", parse_mode='Markdown')
    
    videos = search_youtube(f"Metallica {query}")
    
    if not videos:
        videos = search_youtube_fallback(query)
    
    if videos:
        text = f"🎸 *Найдено {len(videos)} видео:*\n\n"
        for i, video in enumerate(videos[:10], 1):
            text += f"{i}. {format_video(video)}\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━\n🎉 Найденные видео сохранены в базу!"
        
        bot.send_message(message.chat.id, text, parse_mode='Markdown', disable_web_page_preview=True)
        
        for video in videos:
            save_video_to_db(video)
    else:
        bot.send_message(message.chat.id, """😔 Видео не найдено.

Попробуйте другой запрос:
/search Metallica live concert
/search Metallica full show
/search James Hetfield interview""")

@bot.message_handler(commands=['concerts'])
def concerts(message):
    videos = get_concerts()
    if videos:
        text = "🎸 *Концерты Metallica*\n\n"
        for row in videos:
            text += format_video_row(row) + "\n\n"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, """😔 Концерты не найдены.

Используйте /search для поиска:
/search Metallica live concert
/search full show""")

@bot.message_handler(commands=['interviews'])
def interviews(message):
    videos = get_interviews()
    if videos:
        text = "🎤 *Интервью Metallica*\n\n"
        for row in videos:
            text += format_video_row(row) + "\n\n"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, """😔 Интервью не найдены.

Используйте /search:
/search Metallica interview""")

@bot.message_handler(commands=['archive'])
def archive(message):
    concerts = get_concerts()
    interviews = get_interviews()
    text = f"""📦 *Архив Metallica*

🎸 Концертов: {len(concerts)}
🎤 Интервью: {len(interviews)}
📦 Всего: {len(concerts) + len(interviews)}

/search [запрос] - Поиск новых!"""
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

/search [запрос] - Поиск!"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

def format_video_row(row):
    duration = row[7] if row[7] else 0
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    tour = row[5] if row[5] else 'Metallica'
    return f"""🎸 *{row[2]}*
⏱️ {hours}:{minutes:02d} | 🏷️ {tour}
🔗 [Смотреть]({row[3]})"""

@bot.message_handler(func=lambda message: True)
def echo(message):
    if message.text and not message.text.startswith('/'):
        bot.send_message(message.chat.id, "Используйте /search [запрос]\nНапример: /search Metallica Live 2024")
    else:
        bot.send_message(message.chat.id, "Неизвестная команда. /help")

if __name__ == "__main__":
    init_db()
    print("🎸 Metallica Archive Bot запущен!")
    bot.infinity_polling()
