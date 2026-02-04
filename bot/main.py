import telebot
import sqlite3
import requests
import os

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN)

DATABASE = "data/metallica.db"

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
                  quality_tags TEXT)''')
    conn.commit()
    conn.close()

def search_youtube(query):
    """Поиск через RSS ленту YouTube"""
    try:
        url = f"https://www.youtube.com/results?search_query=Metallica+{query.replace(' ', '+')}&sp=EgIYAQ%253D%253D"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            import re
            videos = []
            
            # Ищем видео в HTML
            pattern = r'"videoId":"([^"]+)"'
            ids = re.findall(pattern, response.text)
            
            pattern_title = r'"title":{"runs":\[{"text":"([^"]+)"'
            titles = re.findall(pattern_title, response.text)
            
            pattern_duration = r'"lengthText":{"simpleText":"([^"]+)"'
            durations = re.findall(pattern_duration, response.text)
            
            for i, vid_id in enumerate(ids[:10]):
                if vid_id:
                    title = titles[i] if i < len(titles) else "Metallica Video"
                    duration = parse_duration(durations[i]) if i < len(durations) else 0
                    
                    # Определяем тип
                    content_type = "concert"
                    if any(kw in title.lower() for kw in ["interview", "talk", "conversation", "q&a"]):
                        content_type = "interview"
                    
                    # Определяем тур
                    tour = detect_tour(title)
                    
                    videos.append({
                        "youtube_id": vid_id,
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={vid_id}",
                        "content_type": content_type,
                        "tour_name": tour,
                        "duration_seconds": duration,
                        "quality_tags": "HD" if duration > 1800 else "SD"
                    })
            
            return videos
    except Exception as e:
        print(f"Search error: {e}")
    return []

def parse_duration(duration_str):
    """Парсинг длительности вида '1:23:45' или '23:45'"""
    try:
        parts = duration_str.split(':')
        if len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        return 0
    except:
        return 0

def detect_tour(title):
    title_lower = title.lower()
    tours = {
        "M72 World Tour": ["m72", "72 tour"],
        "WorldWired Tour": ["worldwired", "world wired", "hardwired"],
        "World Magnetic Tour": ["world magnetic", "death magnetic"],
        "Black Album Tour": ["black album"],
        "St. Anger Tour": ["st anger", "st. anger"],
        "Load Tour": ["load tour"],
        "ReLoad Tour": ["reload tour"],
        "Garage Inc.": ["garage inc"],
        "Master of Puppets": ["master of puppets"],
        "Ride the Lightning": ["ride the lightning"],
        "Kill 'Em All": ["kill 'em all", "kill em all"],
    }
    for tour, keywords in tours.items():
        for kw in keywords:
            if kw in title_lower:
                return tour
    return "Metallica"

def save_video(video):
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
    finally:
        conn.close()

def format_video(video):
    duration = video.get('duration_seconds', 0)
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    tour = video.get('tour_name', 'Metallica')
    return f"""🎸 *{video['title']}*
⏱️ {hours}:{minutes:02d} | 🏷️ {tour}
🔗 [Смотреть]({video['url']})"""

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """🎸 *Metallica Archive Bot*

Команды:
/search Metallica Live 2024
/search Metallica interview
/concerts
/interviews
/help""", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, """🎸 *Команды:*

/search [запрос] - Поиск
/concerts - Из базы
/interviews - Из базы
/archive - Архив

Примеры:
/search Metallica Live concert
/search M72 World Tour
/search Lars Ulrich interview""", parse_mode='Markdown')

@bot.message_handler(commands=['search'])
def search(message):
    query = message.text.replace('/search', '').strip()
    if not query:
        bot.send_message(message.chat.id, "Введите: /search [запрос]")
        return
    
    bot.send_message(message.chat.id, f"🔍 Ищу: *{query}*...", parse_mode='Markdown')
    
    videos = search_youtube(query)
    
    if videos:
        text = f"🎸 *Найдено {len(videos)} видео:*\n\n"
        for i, video in enumerate(videos[:10], 1):
            text += f"{i}. {format_video(video)}\n\n"
            save_video(video)
        
        bot.send_message(message.chat.id, text, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, """😔 Ничего не найдено.

Попробуйте:
/search Metallica live concert
/search Metallica full show
/search interview""")

@bot.message_handler(commands=['concerts'])
def concerts(message):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE content_type='concert' ORDER BY duration_seconds DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    
    if rows:
        text = "🎸 *Концерты:*\n\n"
        for row in rows:
            text += f"• {row[2]}\n🔗 {row[3]}\n"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "База пуста. Используйте /search")

@bot.message_handler(commands=['interviews'])
def interviews(message):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE content_type='interview' ORDER BY duration_seconds DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    
    if rows:
        text = "🎤 *Интервью:*\n\n"
        for row in rows:
            text += f"• {row[2]}\n🔗 {row[3]}\n"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "База пуста. Используйте /search")

@bot.message_handler(commands=['archive'])
def archive(message):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM videos WHERE content_type='concert'")
    concerts = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM videos WHERE content_type='interview'")
    interviews = c.fetchone()[0]
    conn.close()
    bot.send_message(message.chat.id, f"""📦 *Архив*

🎸 Концертов: {concerts}
🎤 Интервью: {interviews}
📦 Всего: {concerts + interviews}

/search [запрос] - Поиск!""", parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def echo(m):
    if m.text and not m.text.startswith('/'):
        bot.send_message(m.chat.id, "Используйте /search [запрос]")
    else:
        bot.send_message(m.chat.id, "Неизвестная команда. /help")

if __name__ == "__main__":
    init_db()
    print("🎸 Bot started!")
    bot.infinity_polling()
