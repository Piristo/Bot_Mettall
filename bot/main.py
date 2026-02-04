import telebot
import threading
from telebot import types
import sqlite3
import json
from datetime import datetime
import requests
import time

TOKEN = "YOUR_BOT_TOKEN_HERE"

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

def format_video(row):
    return f"🎸 {row[2]}\n📍 {row[6] if row[6] else 'Unknown'}\n⏱️ {row[7] // 3600 if row[7] else 0}:{(row[7] % 3600) // 60:02d}\n🔗 {row[3]}\n⭐️ {row[8] if row[8] else ''}\n{'-'*20}"

@bot.message_handler(commands=['start'])
def start(message):
    text = """🎸 *Metallica Archive Bot*

Добро пожаловать в архив концертов и интервью Metallica!

Команды:
/concerts - Концерты
/interviews - Интервью
/archive - Архив
/help - Помощь"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['concerts'])
def concerts(message):
    videos = get_concerts()
    if videos:
        text = "🎸 *Концерты Metallica*\n\n"
        for row in videos:
            text += format_video(row) + "\n"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "😔 Концерты не найдены. База пуста.")

@bot.message_handler(commands=['interviews'])
def interviews(message):
    videos = get_interviews()
    if videos:
        text = "🎤 *Интервью Metallica*\n\n"
        for row in videos:
            text += format_video(row) + "\n"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "😔 Интервью не найдены. База пуста.")

@bot.message_handler(commands=['help'])
def help(message):
    text = """🎸 *Команды:*

/start - Старт
/concerts - Концерты
/interviews - Интервью
/archive - Архив
/stats - Статистика
/refresh - Обновить базу"""
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
📦 Всего: {concerts + interviews}"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['archive'])
def archive(message):
    concerts = get_concerts()
    interviews = get_interviews()
    text = f"📦 *Архив Metallica*\n\n🎸 Концертов: {len(concerts)}\n🎤 Интервью: {len(interviews)}"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['refresh'])
def refresh(message):
    bot.send_message(message.chat.id, "🔄 Обновление базы...\n\nТребуется YouTube API или Invidious.")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, "Неизвестная команда. /help")

if __name__ == "__main__":
    init_db()
    print("🎸 Metallica Archive Bot запущен!")
    bot.infinity_polling()
